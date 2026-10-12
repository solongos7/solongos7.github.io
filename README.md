# SolongoS :: 무지개 나라

GitHub Pages와 Jekyll로 만든 개인 블로그입니다. 사이트 주소는 <https://solongos7.github.io/>입니다.

## 새 글 추가하기

1. 블로그 상단의 **새 글 쓰기** 메뉴를 누릅니다.
2. 제목, 분류, 날짜, 본문을 입력하고 **글 파일 내려받기**를 누릅니다. 파일 이름과 글에 필요한 설정은 자동으로 만들어집니다.
3. 같은 화면의 **GitHub에 파일 올리기**를 누르고, 내려받은 `.md` 파일을 업로드합니다. **Commit changes**를 누르면 글이 게시됩니다.

GitHub에는 이 저장소에 쓸 수 있는 계정으로 로그인해야 합니다. `main` 브랜치에 파일이 올라간 뒤 GitHub Pages가 다시 빌드되면 홈의 **최근 글**에 표시됩니다.

## 글 관리하기

글을 수정하거나 삭제하려면 GitHub의 [`_posts` 폴더](https://github.com/solongos7/solongos7.github.io/tree/main/_posts)에서 해당 파일을 엽니다. 연필 아이콘으로 수정하고, 파일 메뉴에서 삭제할 수 있습니다. 수정 후에도 **Commit changes**를 눌러야 사이트에 반영됩니다.

글 형식을 직접 편집하고 싶다면 `_posts` 폴더에 `YYYY-MM-DD-english-slug.md` 파일을 만들어 `layout: post`, `title`, `date`가 포함된 Jekyll 머리말을 작성하면 됩니다. 홈의 소개 문구는 `index.html`, 색상과 화면 구성은 `assets/css/style.css`에서 바꿀 수 있습니다.

## 신화이야기 자동 게시

상단 **신화이야기** 메뉴는 Hermes가 매일 생성하는 그리스·로마 신화 알림을 모읍니다.
Linux Hermes의 별도 스크립트 cron이 매일 **09:00 KST**에 시작해 당일 알림의 완성을 기다린 뒤 글을 커밋하고 `main`으로 푸시합니다. 원래 신화 알림 cron과 Telegram 전달은 유지됩니다.

`scripts/publish_mythology.py`는 신화 작업의 출력 파일과 Hermes 대화 DB에서 완성된 응답만 읽습니다. 같은 날짜의 동일한 글은 한 번만 가져오며, 내용이 다른 재실행 결과는 별도로 보존합니다. 빈 결과·실패·작성 중 메모와 실행 프롬프트는 게시하지 않습니다. 이미 가져온 글의 수동 편집도 덮어쓰지 않습니다.

- 점검: `python3 scripts/publish_mythology.py`
- 가져오기: `python3 scripts/publish_mythology.py --import-only`
- 커밋·푸시: `python3 scripts/publish_mythology.py --publish`
- 검증: `python3 -m unittest discover -s tests -v`

당일 완성된 글이 45분 안에 나오지 않으면 게시 작업은 실패로 기록되며 내용을 임의로 만들지 않습니다. 다른 수정이 남아 있는 작업 폴더도 자동 커밋하지 않습니다. 푸시 실패 후 남은 신화 게시 커밋은 다음 실행에서 다시 푸시하며, 다른 게시자가 원격 `main`을 갱신한 경우 생성된 신화 글만 재정렬합니다.
