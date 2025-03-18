# WIZ Electron Plugin

## Installation

1. 우측 하단 System Setting > IDE Menu에 기존의 Explore 제거 후 아래 내용 추가

```json
{
    "name": "Electron Explore",
    "id": "electron.app.explore",
    "icon": "fa-solid fa-atom",
    "width": 360
},
```

2. Electron Explore > rebuild 실행

3. Electron Explore > electron에서 파일 4개 확인

- `.env`, `index.js`, `paths.js`, `preload.mjs`

4. `.env` 수정

5. `package.json` 내용 확인

- "name"
    - 왠만하면 값 바꾸는 것을 추천
- "version"
    - 버전 지정
- "main"
    - 새로 추가된 필드
    - "public/index.js" 값 확인
- "scripts"
    - el:dev, el:build 들어가있는지 확인
        - "el:dev": "dotenv -e electron/.env -- electron ."
        - "el:build": "electron-builder"
- "type"
    - 새로 추가된 필드
    - "module" 값 확인
- "dependencies"
    - electron-is-dev 확인
- "devDependencies"
    - dotenv-cli, electron, electron-builder 확인
