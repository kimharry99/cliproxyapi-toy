# EasyCLIProxyAPI 메시지 toy

실행 중인 EasyCLIProxyAPI(`http://127.0.0.1:18317/v1`)에 메시지를 보내고
assistant의 답장을 출력합니다. Python 표준 라이브러리만 사용합니다.
프록시 실행과 계정 인증은 외부 EasyCLIProxyAPI에서 관리합니다.

```bash
cd cliproxyapi-toy
IFS= read -r -s -p 'Local proxy key: ' CLIPROXY_CLIENT_KEY
printf '\n'
export CLIPROXY_CLIENT_KEY
python3 client.py
unset CLIPROXY_CLIENT_KEY
```

`CLIPROXY_CLIENT_KEY`에는 실행 중인 프록시의 로컬 접속 키를 입력합니다.
이 클라이언트는 계정 토큰이나 앱 설정 파일을 읽지 않습니다.

`client.py`의 흐름은 환경변수에서 키 읽기 → `model/messages` JSON 구성 →
`POST /v1/chat/completions` → `choices[0].message.content` 출력입니다.
`main()`의 `message` 변수에 적은 메시지를 보내고, 응답이 완성된 뒤 한 번에 출력합니다.

| 모듈 상수 | 값 |
|---|---|
| `BASE_URL` | `http://127.0.0.1:18317/v1` |
| `MODEL` | `gpt-6-luna` |
| `TIMEOUT_SECONDS` | `180` |

메시지는 `main()`의 `message = "Hello. Please reply in one sentence."`에서 수정합니다.
모델은 요청에 사용할 ID로 고정되어 있으며, 현재 계정의 호출 가능 여부를 검증한 것은
아닙니다. timeout은 소켓의 블로킹 작업에 적용되며 전체 요청 시간 제한은 아닙니다.
자동 재시도는 없습니다. HTTP 오류는 상태코드를 표시하고 종료코드 1을 반환하며,
그 밖의 라이브러리·응답 처리 예외는 그대로 전파합니다.
