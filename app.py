import http.server
import socketserver
import json
import socket
import urllib.parse
from src.parser import process_text_input
from src.ics_calendar import generate_ics_from_schedule

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text2Schedule - 일정 문자 ➔ ISO JSON & 캘린더 변환기</title>
    <style>
        :root {
            --primary: #4F46E5;
            --primary-hover: #4338CA;
            --bg: #F9FAFB;
            --card-bg: #FFFFFF;
            --text: #1F2937;
            --text-muted: #6B7280;
            --border: #E5E7EB;
            --accent: #10B981;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        body { background-color: var(--bg); color: var(--text); padding: 16px; display: flex; justify-content: center; }
        .container { max-width: 680px; width: 100%; }
        header { text-align: center; margin-bottom: 20px; }
        header h1 { font-size: 1.5rem; color: var(--primary); margin-bottom: 4px; }
        header p { font-size: 0.9rem; color: var(--text-muted); }
        .card { background: var(--card-bg); border-radius: 12px; padding: 18px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 16px; border: 1px solid var(--border); }
        label { font-weight: 600; display: block; margin-bottom: 8px; font-size: 0.95rem; }
        textarea { width: 100%; height: 150px; padding: 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; resize: vertical; outline: none; transition: border-color 0.2s; }
        textarea:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79,70,229,0.1); }
        .btn-group { display: flex; flex-direction: column; gap: 10px; margin-top: 12px; }
        @media (min-width: 480px) { .btn-group { flex-direction: row; } }
        button { flex: 1; padding: 12px 16px; border: none; border-radius: 8px; background: var(--primary); color: white; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        button:hover { background: var(--primary-hover); }
        button.secondary { background: #6B7280; }
        button.secondary:hover { background: #4B5563; }
        button.success { background: var(--accent); }
        button.success:hover { background: #059669; }
        .loading { display: none; text-align: center; padding: 20px; color: var(--primary); font-weight: 600; }
        .result-item { background: #F3F4F6; border-left: 4px solid var(--primary); border-radius: 6px; padding: 14px; margin-bottom: 14px; }
        .result-item h3 { font-size: 1.1rem; margin-bottom: 8px; color: var(--primary); }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; background: #E0E7FF; color: var(--primary); margin-bottom: 8px; }
        .badge.warning { background: #FEF3C7; color: #D97706; }
        .field { margin-bottom: 6px; font-size: 0.9rem; word-break: break-all; }
        .field-label { font-weight: 600; color: var(--text-muted); display: inline-block; min-width: 100px; }
        .iso-tag { font-family: monospace; background: #E5E7EB; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; color: #111827; }
        pre { background: #1E293B; color: #F8FAFC; padding: 14px; border-radius: 8px; overflow-x: auto; font-size: 0.85rem; max-height: 250px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📅 Text2Schedule</h1>
            <p>문자 메시지 ➔ ISO 8601 일정 JSON 및 캘린더(.ics) 자동 생성</p>
        </header>

        <div class="card">
            <label for="msgInput">📲 휴대폰 안내 문자 메시지 입력</label>
            <textarea id="msgInput" placeholder="교육, 행사, 예약 등의 문자 내용을 복사하여 붙여넣으세요..."></textarea>
            <div class="btn-group">
                <button id="extractBtn" onclick="extractSchedule()">⚡ AI 일정 분석 및 ISO 변환</button>
            </div>
        </div>

        <div id="loading" class="loading">
            ⏳ AI가 일정 정보 분석 및 ISO 8601 포맷으로 변환 중입니다...
        </div>

        <div id="resultContainer" style="display: none;">
            <div class="card">
                <h2>🗓️ ISO 8601 일정 정보</h2>
                <div id="scheduleCards" style="margin-top: 14px;"></div>
                
                <div class="btn-group">
                    <button class="success" onclick="downloadICS()">📥 .ics 캘린더 파일 다운로드 (핸드폰 등록용)</button>
                    <button class="secondary" onclick="copyJSON()">📋 ISO JSON 복사</button>
                </div>
            </div>

            <div class="card">
                <h3>📄 원본 ISO 8601 JSON 데이터</h3>
                <pre id="jsonPreview"></pre>
            </div>
        </div>
    </div>

    <script>
        let currentSchedules = [];

        async function extractSchedule() {
            const text = document.getElementById("msgInput").value.trim();
            if (!text) {
                alert("안내 문자 내용을 입력해주세요.");
                return;
            }

            document.getElementById("loading").style.display = "block";
            document.getElementById("resultContainer").style.display = "none";

            try {
                const response = await fetch("/api/parse", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text })
                });

                const data = await response.json();
                currentSchedules = data.schedules;
                renderResults(currentSchedules);
            } catch (err) {
                alert("일정 분석 중 오류가 발생했습니다: " + err.message);
            } finally {
                document.getElementById("loading").style.display = "none";
            }
        }

        function renderResults(schedules) {
            const cardsDiv = document.getElementById("scheduleCards");
            cardsDiv.innerHTML = "";

            if (!schedules || schedules.length === 0) {
                cardsDiv.innerHTML = "<p style='color: var(--text-muted);'>추출된 일정이 없습니다.</p>";
                return;
            }

            schedules.forEach((item, idx) => {
                const card = document.createElement("div");
                card.className = "result-item";
                
                let reviewBadge = item.needs_review 
                    ? `<span class="badge warning">⚠️ 검토 필요: ${item.review_reason || '확인 요망'}</span>`
                    : `<span class="badge">✅ ISO 규격 확인 완료</span>`;

                card.innerHTML = `
                    ${reviewBadge}
                    <h3>${idx + 1}. ${item.summary || '제목 없음'}</h3>
                    <div class="field"><span class="field-label">ISO 시작시각:</span> <span class="iso-tag">${item.start_iso || '미정'}</span></div>
                    <div class="field"><span class="field-label">ISO 종료시각:</span> <span class="iso-tag">${item.end_iso || '미정'}</span></div>
                    <div class="field"><span class="field-label">일정 날짜:</span> ${item.date_iso || '미정'}</div>
                    <div class="field"><span class="field-label">장소:</span> ${item.location || '미정'}</div>
                    <div class="field"><span class="field-label">메모/안내:</span> ${item.description || '없음'}</div>
                `;
                cardsDiv.appendChild(card);
            });

            document.getElementById("jsonPreview").textContent = JSON.stringify(schedules, null, 2);
            document.getElementById("resultContainer").style.display = "block";
        }

        function downloadICS() {
            if (!currentSchedules || currentSchedules.length === 0) return;
            fetch("/api/ics", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ schedules: currentSchedules })
            })
            .then(res => res.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "schedule.ics";
                document.body.appendChild(a);
                a.click();
                a.remove();
            });
        }

        function copyJSON() {
            const jsonText = JSON.stringify(currentSchedules, null, 2);
            navigator.clipboard.writeText(jsonText).then(() => {
                alert("ISO JSON 데이터가 클립보드에 복사되었습니다!");
            });
        }
    </script>
</body>
</html>
"""

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """모바일 웹 UI 서버 요청 핸들러 (HTTP GET/POST API 처리)"""
    
    def do_GET(self):
        """웹 페이지 메인 화면(HTML) 응답"""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        else:
            self.send_error(404, "페이지를 찾을 수 없습니다.")

    def do_POST(self):
        """API 요청 처리 (/api/parse : AI 일정 추출, /api/ics : .ics 파일 생성)"""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        # 1. 문자 텍스트 ➔ AI 일정 정보 및 ISO 파싱 API
        if self.path == "/api/parse":
            text = data.get("text", "")
            schedules, _ = process_text_input(input_text=text)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            response_payload = json.dumps({"schedules": schedules}, ensure_ascii=False)
            self.wfile.write(response_payload.encode("utf-8"))

        # 2. 일정 객체 ➔ .ics 캘린더 파일 생성 및 다운로드 API
        elif self.path == "/api/ics":
            schedules = data.get("schedules", [])
            ics_content = generate_ics_from_schedule(schedules)
            
            self.send_response(200)
            self.send_header("Content-Type", "text/calendar; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=schedule.ics")
            self.end_headers()
            self.wfile.write(ics_content.encode("utf-8"))

        else:
            self.send_error(404, "API 경로를 찾을 수 없습니다.")

def get_local_ip():
    """스마트폰 접속을 위한 PC의 현재 사설 IP 주소(예: 192.168.X.X)를 조회합니다."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_web_server(port: int = 8000):
    """모바일 웹 서버를 구동합니다."""
    handler = RequestHandler
    local_ip = get_local_ip()
    with socketserver.TCPServer(("", port), handler) as httpd:
        print("\n=======================================================")
        print("🚀 Text2Schedule 모바일 웹 서버 실행 완료!")
        print("=======================================================")
        print(f"💻 PC 브라우저 접속:     http://localhost:{port}")
        print(f"📱 스마트폰 접속(동일 Wi-Fi): http://{local_ip}:{port}")
        print("=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버가 종료되었습니다.")

if __name__ == "__main__":
    run_web_server()
