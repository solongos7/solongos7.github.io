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
