import time
from unittest.mock import patch

from orchestrator import ZeussOrchestrator
from llm_router import LLMRouter

def run_benchmark():
    start_time = time.time()

    # We patch multiple components to ensure a fully mocked execution
    with patch('llm_router.LLMRouter.search_authoritative_facts') as mock_search, \
         patch('llm_router.LLMRouter.synthesize_report_section') as mock_synth, \
         patch('llm_router.LLMRouter.qa_verify_report') as mock_qa, \
         patch('orchestrator.requests.post') as mock_post:

        # Setup mock returns
        mock_search.return_value = [{"fact": "Mock fact 1", "numeric_data": "100", "source_url": "http://mock.gov", "source_domain": "mock.gov", "topic_area": "Mock"}]
        mock_synth.return_value = "Mocked draft text of the report."
        mock_qa.return_value = {"approved": True, "confidence_score": 100, "summary": "Mock summary", "critique": "", "audited_claims": []}

        # We need the orchestrator to go through nodes A, B, C, D, E and FINISH
        # So we supply a sequence of commands
        class MockResponse:
            def __init__(self, commands):
                self.commands = commands
                self.index = 0
            def json(self):
                cmd = self.commands[self.index]
                self.index = min(self.index + 1, len(self.commands) - 1)
                return {"choices": [{"message": {"content": cmd}}]}
            def raise_for_status(self):
                pass

        commands = [
            "RUN_NODE_A(1)",
            "RUN_NODE_B(1)",
            "RUN_NODE_C(1)",
            "RUN_NODE_D()",
            "RUN_NODE_E()",
            "FINISH(Pipeline finished)"
        ]

        mock_post.return_value = MockResponse(commands)

        # Also patch Node D and Node E to not actually generate PDFs or do more work
        with patch('main.MultiChapterPipelineEngine.run_node_d_institutional_publisher') as mock_node_d, \
             patch('main.MultiChapterPipelineEngine.run_node_e_commercial_council') as mock_node_e:

            mock_node_d.return_value = True
            mock_node_e.return_value = "PUBLISH"

            orch = ZeussOrchestrator("AI Benchmark Test")

            # The orchestrator's execute_mission method has an infinite loop
            # but it breaks when it hits FINISH
            orch.execute_mission()

    end_time = time.time()
    print(f"Mocked Pipeline Execution Time: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
