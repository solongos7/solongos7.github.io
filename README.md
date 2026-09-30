# SolongoS :: 무지개 나라

GitHub Pages와 Jekyll로 만든 개인 블로그입니다. 사이트 주소는 <https://solongos7.github.io/>입니다.

## 새 글 추가하기

1. 블로그 상단의 **새 글 쓰기** 메뉴를 누르고 GitHub에 로그인합니다. `_posts` 폴더에 `YYYY-MM-DD-english-slug.md` 형식으로 파일을 만듭니다. 예: `_posts/2026-10-01-new-story.md`.
2. 파일 맨 위에 아래 내용을 넣고, 그 아래에 Markdown으로 본문을 작성합니다.

   ```markdown
   ---
   layout: post
   title: "새 글 제목"
   date: 2026-10-01
   category: "일상"
   description: "글을 짧게 소개하는 문장"
   ---

   여기에 첫 문단을 작성합니다.

   ## 소제목

   이어지는 내용을 작성합니다.
   ```

3. `main` 브랜치에 변경 사항을 올리면 GitHub Pages가 사이트를 다시 빌드합니다. 새 글은 홈의 **최근 글**에 날짜순으로 자동 표시됩니다.

**새 글 쓰기** 메뉴는 GitHub의 파일 작성 화면으로 연결됩니다. GitHub Pages 자체에는 글을 저장하는 관리자 기능이 없으며, 저장하려면 이 저장소에 쓸 수 있는 GitHub 계정으로 로그인해야 합니다.

글을 수정할 때는 해당 Markdown 파일을 고치면 됩니다. 홈의 소개 문구는 `index.html`, 색상과 화면 구성은 `assets/css/style.css`에서 바꿀 수 있습니다.
