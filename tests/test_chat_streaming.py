# -*- coding: utf-8 -*-
"""
KIỂM THỬ SSE STREAMING TỪNG TOKEN (/api/v1/chat/stream & stream_tourism_agent_response)
"""
import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class TestChatStreaming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.rag import agent_graph
        cls.ag = agent_graph

    def _initial_state(self, query, weather=None):
        return {
            "query": query, "locality": "Thành phố Huế", "preferences": {}, "image_base64": None,
            "image_detected": None, "visual_matches": None, "visual_confidence": 0.0,
            "target_dish": None, "target_place": None, "matched_places": [],
            "nearby_map": {}, "dishes_map": {}, "reviews": [], "web_results": [],
            "confidence_score": 0.0, "route_taken": "local_knowledge",
            "formatted_context": "", "final_answer": "", "graph_trace": [],
            "user_lat": None, "user_lng": None, "language": "vi",
            "session_id": None, "history": [], "session_context": None,
            "weather_context": weather, "resolved_query": None, "anaphora": None,
        }

    def test_stream_helper_emits_token_chunks_then_final_state(self):
        class FakeStreamingLLM:
            def stream(self, messages):
                for part in ["Dạ, ", "**Đại Nội Huế** ", "có giá vé 200.000 VNĐ."]:
                    yield type("C", (), {"content": part})()

        orig = self.ag.llm
        self.ag.llm = FakeStreamingLLM()
        try:
            events = list(self.ag.stream_tourism_agent_response(
                self._initial_state("Giá vé vào Đại Nội Huế bao nhiêu?")
            ))
            tokens = [p for k, p in events if k == "token"]
            finals = [p for k, p in events if k == "final"]
            self.assertEqual(tokens, ["Dạ, ", "**Đại Nội Huế** ", "có giá vé 200.000 VNĐ."])
            self.assertEqual(len(finals), 1)
            self.assertIn("200.000 VNĐ", finals[0]["final_answer"])
            self.assertGreater(len(finals[0]["matched_places"]), 0)
        finally:
            self.ag.llm = orig

    def test_stream_helper_direct_weather_skips_llm(self):
        events = list(self.ag.stream_tourism_agent_response(
            self._initial_state(
                "Thời tiết Huế hôm nay thế nào?",
                weather={"temp": 24, "humidity": 90, "precipitation": 0.6, "weather_code": 80},
            )
        ))
        tokens = [p for k, p in events if k == "token"]
        finals = [p for k, p in events if k == "final"]
        self.assertEqual(len(tokens), 1)
        self.assertIn("24°C", tokens[0])
        self.assertEqual(finals[0]["final_answer"], tokens[0])

    def test_fastapi_chat_stream_endpoint_sse_format(self):
        from src.app.routes.chat_route import chat_assistant_stream, format_chat_sse_events
        from src.app.schemas.chat_schema import ChatRequest

        class FakeStreamingLLM:
            def stream(self, messages):
                for part in ["Chào bạn! ", "Bạn nên ghé **Đại Nội Huế**."]:
                    yield type("C", (), {"content": part})()

        orig = self.ag.llm
        self.ag.llm = FakeStreamingLLM()
        try:
            req = ChatRequest(query="Đại Nội Huế ở đâu?")
            resp = chat_assistant_stream(req)
            self.assertEqual(resp.media_type, "text/event-stream")
            self.assertEqual(resp.headers.get("x-accel-buffering"), "no")
            self.assertEqual(resp.headers.get("cache-control"), "no-cache")

            body = "".join(format_chat_sse_events(req))
            self.assertIn("event: token", body)
            self.assertIn("event: done", body)
            done_block = [b for b in body.split("\n\n") if "event: done" in b][0]
            data_line = [ln[5:].strip() for ln in done_block.splitlines() if ln.startswith("data:")][0]
            done_json = json.loads(data_line)
            self.assertEqual(done_json["status"], "success")
            self.assertIn("Đại Nội Huế", done_json["answer"])
        finally:
            self.ag.llm = orig


if __name__ == "__main__":
    unittest.main(verbosity=2)

