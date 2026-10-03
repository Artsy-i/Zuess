import os
import json
import requests
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import real Zeuss logic
from llm_router import LLMRouter
from main import CHAPTERS, MultiChapterPipelineEngine, PipelineDashboard

load_dotenv()

class ZeussOrchestrator:
    def __init__(self, topic: str):
        self.topic = topic
        self.api_key = os.getenv("OPENROUTER_ORCHESTRATOR_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "nvidia/nemotron-3-ultra-550b-a55b:free"
        self.console = Console()
        
        self.router = LLMRouter()
        self.chapters_state = {ch["id"]: {"meta": ch, "facts": [], "draft": "", "approved": False} for ch in CHAPTERS}
        
        self.history = [
            {
                "role": "system",
                "content": (
                    "You are the CHIEF ORCHESTRATOR of the Zeuss Autonomous B2B Intelligence Pipeline. "
                    "Your job is to manage worker nodes (A, B, C, D, E) to produce a 4-chapter report. "
                    "You do NOT write the report yourself. You issue commands to nodes, read their short feedback, and decide what to do next. "
                    "Available Commands:\n"
                    "- RUN_NODE_A(chapter_id) -> Triggers DuckDuckGo search and extracts JSON facts.\n"
                    "- RUN_NODE_B(chapter_id, instructions) -> Synthesizes facts into draft. Provide rewrite instructions if Node C failed.\n"
                    "- RUN_NODE_C(chapter_id) -> Audits the draft. If it fails, command Node B to rewrite.\n"
                    "- RUN_NODE_D() -> Compiles final PDF (Only call when Chapters 1-4 are all approved).\n"
                    "- RUN_NODE_E() -> Submits the compiled report to the Commercial Council for a final Chairman's Verdict (Only call after Node D).\n"
                    "- FINISH(summary) -> End the pipeline. The summary should include the Chairman's final verdict and your review of it.\n\n"
                    "Reply ONLY with the exact command string you want to execute next, e.g., 'RUN_NODE_A(1)' or 'RUN_NODE_B(1, Rewrite the growth numbers)'. "
                    "Do not include any conversational text outside the command."
                )
            },
            {
                "role": "user",
                "content": f"MISSION START: The user requested a report on '{self.topic}'. Begin by gathering facts for Chapter 1."
            }
        ]
        
        self.current_task = "Initializing Orchestrator..."
        self.current_process = "Booting..."

    def _call_llm(self) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": self.history,
            "temperature": 0.0
        }
        try:
            resp = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _generate_ui(self) -> Panel:
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold yellow", width=18)
        table.add_column(style="white")
        table.add_row("Mission:", f"[bold cyan]{self.topic}[/bold cyan]")
        table.add_row("Current Task:", self.current_task)
        table.add_row("Process:", f"[bold green]{self.current_process}[/bold green]")
        
        approved_count = sum(1 for ch in self.chapters_state.values() if ch["approved"])
        table.add_row("Progress:", f"{approved_count}/4 Chapters Approved")
        
        return Panel(table, title="[bold cyan]Zeuss Orchestrator Monitor[/bold cyan]", border_style="cyan")

    def execute_mission(self):
        from rich.live import Live
        with Live(self._generate_ui(), refresh_per_second=4, console=self.console) as live:
            
            while True:
                self.current_process = "Orchestrator Thinking..."
                live.update(self._generate_ui())
                
                command = self._call_llm()
                self.history.append({"role": "assistant", "content": command})
                
                self.current_task = f"Executing: {command}"
                self.current_process = "Waiting for Node..."
                live.update(self._generate_ui())
                
                feedback = ""
                try:
                    if command.startswith("RUN_NODE_A"):
                        ch_id = int(command.split("(")[1].split(")")[0])
                        ch = self.chapters_state[ch_id]["meta"]
                        facts = self.router.search_authoritative_facts(
                            topic=self.topic, chapter_title=ch["title"], chapter_focus=ch["focus"]
                        )
                        self.chapters_state[ch_id]["facts"] = facts
                        feedback = f"Node A completed. Found {len(facts)} facts across web sources."
                        
                    elif command.startswith("RUN_NODE_B"):
                        args_str = command.split("(", 1)[1].rsplit(")", 1)[0]
                        args = [arg.strip() for arg in args_str.split(",", 1)]
                        ch_id = int(args[0])
                        instructions = args[1] if len(args) > 1 else None
                        ch = self.chapters_state[ch_id]["meta"]
                        facts = self.chapters_state[ch_id]["facts"]
                        
                        draft = self.router.synthesize_report_section(
                            topic=self.topic, facts_data=facts, chapter_title=ch["title"], chapter_focus=ch["focus"], qa_critique=instructions
                        )
                        self.chapters_state[ch_id]["draft"] = draft
                        word_count = len(draft.split())
                        feedback = f"Node B completed draft ({word_count} words)."
                        
                    elif command.startswith("RUN_NODE_C"):
                        ch_id = int(command.split("(")[1].split(")")[0])
                        ch = self.chapters_state[ch_id]["meta"]
                        draft = self.chapters_state[ch_id]["draft"]
                        facts = self.chapters_state[ch_id]["facts"]
                        
                        qa_result = self.router.qa_verify_report(
                            topic=self.topic, draft_text=draft, facts_data=facts, chapter_title=ch["title"]
                        )
                        
                        score = qa_result.get("confidence_score", 100)
                        approved = qa_result.get("approved", False)
                        if approved:
                            self.chapters_state[ch_id]["approved"] = True
                            feedback = f"Node C PASS. Score: {score}/100. No hallucinations found."
                        else:
                            critique = qa_result.get("critique", "Unverified claims detected.")
                            feedback = f"Node C FAIL. Score: {score}/100. Reason: {critique}"
                            
                    elif command.startswith("RUN_NODE_D"):
                        # We use the legacy engine for Node D to compile PDF
                        engine = MultiChapterPipelineEngine(topic=self.topic, auto_approve=True)
                        # Re-format state for Node D
                        for cid, data in self.chapters_state.items():
                            engine.chapters_results.append({
                                "id": cid, "title": data["meta"]["title"], 
                                "qa_result": {"confidence_score": 100}, 
                                "draft_text": data["draft"], "facts_data": data["facts"]
                            })
                        live.stop()
                        engine.run_node_d_institutional_publisher(self.console)
                        feedback = "Node D compiled PDF successfully."
                        # Resume Live
                        live.start()
                        
                    elif command.startswith("RUN_NODE_E"):
                        engine = MultiChapterPipelineEngine(topic=self.topic, auto_approve=True)
                        # Re-format state for Node E
                        for cid, data in self.chapters_state.items():
                            engine.chapters_results.append({
                                "id": cid, "title": data["meta"]["title"], 
                                "qa_result": {"confidence_score": 100}, 
                                "draft_text": data["draft"], "facts_data": data["facts"]
                            })
                        live.stop()
                        verdict = engine.run_node_e_commercial_council(self.console)
                        feedback = f"Node E completed. Chairman Verdict received: {verdict}"
                        live.start()

                    elif command.startswith("FINISH"):
                        live.stop()
                        summary = command[7:-1] if "(" in command else command.replace("FINISH", "")
                        self.console.print("\n[bold green]MISSION COMPLETE[/bold green]")
                        self.console.print(Panel(summary, title="Final Orchestrator Run Report"))
                        
                        os.makedirs("logs", exist_ok=True)
                        with open("logs/orchestrator_final_report.md", "w", encoding="utf-8") as f:
                            f.write(f"# Zeuss Orchestrator Final Report\n\n**Topic:** {self.topic}\n\n**Summary:**\n{summary}")
                        
                        break
                    else:
                        feedback = "Invalid command format. Please use RUN_NODE_X() format."
                except Exception as e:
                    feedback = f"SYSTEM ERROR while executing {command}: {str(e)}"
                
                self.history.append({"role": "user", "content": feedback})
                
if __name__ == "__main__":
    orch = ZeussOrchestrator("AI Supply Chain 2026")
    orch.execute_mission()

