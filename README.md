# WIZ Electron Plugin

## Installation

1. project 리빌드 실행

2. 우측 하단 System Setting > IDE Menu에 아래 내용 추가

```json
{
    "name": "Electron Explore",
    "id": "electron.app.explore",
    "icon": "fa-solid fa-atom",
    "width": 240
},
```

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

6. angular > `wiz.ts` 수정

- 맨 아래의 url, call 함수 주석처리(or 삭제) 후 아래 코드 추가

```typescript
public server = {
    url: (function_name: string) => {
        let base = window.env.API_BASE;
        if (base.endsWith("/")) base = base.slice(0, -1);
        if (function_name[0] == "/") function_name = function_name.substring(1);
        return `${base}/api/${this.namespace}/${function_name}`;
    },
    call: (function_name: string, data = {}, options = {}) => {
        let ajax = {
            url: this.server.url(function_name),
            type: "POST",
            data: data,
            ...options,
        };

        return new Promise((resolve) => {
            $.ajax(ajax).always(function (res) {
                resolve(res);
            });
        });
    },
};

public send(name, ...data) {
    window.api.send(name, ...data);
}
public receive(name, callback) {
    if (!callback) return;
    window.api.receive(name, callback);
}

public async electron(name, ...data) {
    return new Promise((resolve) => {
        this.receive(name, resolve);
        this.send(name, ...data);
    });
}

public url(function_name: string) {
    return `api.${this.namespace}.${function_name}`;
}

public call(function_name: string, ...params) {
    return this.electron(this.url(function_name), ...params);
}
```

7. angular > `index.pug` 수정

- base의 href값을 "/" -> "./" 로 변경
