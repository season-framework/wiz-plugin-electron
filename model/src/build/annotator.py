import re

Namespace = wiz.ide.plugin.model("src/build/namespace")

class Definition:
    def directives(self, code):
        result = dict()
        pattern = re.compile(r'@directives\(([^\)]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile(r'(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result

    def dependencies(self, code):
        result = dict()
        pattern = re.compile(r'@dependencies\(([^\)]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile(r'(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result

    def directives(self, code):
        result = dict()
        pattern = re.compile(r'@directives\(([^\)]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile(r'(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result

    def ngComponentDesc(self, code):
        res = dict(inputs=[], outputs=[])
        def convert(match_obj):
            val = match_obj.group(1).replace(" ", "")
            res['inputs'].append(val)
            return val
        pattern = re.compile(r'@Input\(\)([^=\:\n\;]*)')
        re.sub(pattern, convert, code)
        
        def convert(match_obj):
            val = match_obj.group(1).replace(" ", "")
            res['outputs'].append(val)
            return val
        pattern = re.compile(r'@Output\(\)([^=\:\n\;]*)')
        re.sub(pattern, convert, code)
        
        return res

class Injection:       
    def app(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val.split("/")) > 1:
                val = val.replace("/directive", "/app.directive")
                return f'"src/app/{val}"'
            return f'"src/app/{val}/{val}.component"'
        patterns = [r'"@wiz\/app\/(.*)"', r"'@wiz\/app\/(.*)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        return code
    
    def libs(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            return f'"src/libs/{val}"'
        patterns = [r'"@wiz\/libs\/(.*)"', r"'@wiz\/libs\/(.*)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        return code

    def namespace(self, code, app_id):
        if app_id is None: return code
        def convert(match_obj):
            return app_id
        pattern = r'@wiz.namespace\((.*)\)'
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.namespace", app_id)
        return code

    def cwd(self, code, app_id):
        if app_id is None: return code
        def convert(match_obj):
            val = match_obj.group(1)
            val = val.replace("directive", "app.directive")
            return f'"src/app/{app_id}/{val}"'
        patterns = [r'"@wiz\/cwd\/(.*)"', r"'@wiz\/cwd\/(.*)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        return code

    def baseuri(self, code, baseuri):
        if baseuri is None: return code
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val) > 0:
                if val[0] == "/":
                    val = val[1:]
                return baseuri + "/" + val
            return baseuri
        pattern = r'@wiz.baseuri\((.*)\)'
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.baseuri", baseuri)
        return code

    def dependencies(self, code):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile(r'@dependencies\(([^\)]*)\)', re.DOTALL)
        code = re.sub(pattern, convert, code)
        return code
    
    def directives(self, code):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile(r'@directives\(([^\)]*)\)', re.DOTALL)
        code = re.sub(pattern, convert, code)
        return code

    def declarations(self, code, declarations):
        if declarations is None: return code
        def convert(match_obj):
            return declarations
        patterns = [r'"@wiz.declarations\((.*)\)"', r"'@wiz.declarations\((.*)\)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        code = code.replace("'@wiz.declarations'", declarations)
        code = code.replace('"@wiz.declarations"', declarations)
        return code

    def imports(self, code, imports):
        if imports is None: return code
        def convert(match_obj):
            return imports
        patterns = [r'"@wiz.imports\((.*)\)"', r"'@wiz.imports\((.*)\)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        code = code.replace("'@wiz.imports'", imports)
        code = code.replace('"@wiz.imports"', imports)
        return code
    
    def route(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            return 'component: ' + Namespace.componentName(val) + "Component"
        pattern = r"component.*:.*'(.*)'"
        code = re.sub(pattern, convert, code)
        pattern = r'component.*:.*"(.*)"'
        code = re.sub(pattern, convert, code)
        code = code.replace("'component", "component")
        code = code.replace('"component', "component")
        return code

class API:
    def __init__(self):
        # arrow function
        self.reg1 = re.compile(r'^const\s([a-zA-Z\d]+)\s*=\s*\(.*\)\s*=>\s*\{\s*$')
        # common function
        self.reg2 = re.compile(r'^function\s*([a-zA-Z\d]+)\s*\(.*\)\s*\{\s*$')

    def find_functions(self, code):
        lines = code.split("\n")
        arr = []
        for line in lines:
            try:
                res = self.reg1.match(line)
                if res is None: res = self.reg2.match(line)
            except:
                res = None
            if res is None: continue
            arr.append(res.group(1))
        return arr

    def functions(self, code, fnlist):
        txt = ", ".join(fnlist)
        code = code + f'\nexport default {{ {txt} }}\n'
        return code

    def events(self, fnlist, namespace):
        template = """ipcMain.on("api.<NAMESPACE>.<APINAME>", async (e, ...params) => {
    try {
        const fn = await import(path.join(appPath, "<NAMESPACE>", "api.js"));
        if (!fn.default) throw new Error(`Not exist export default`);
        const api = "<APINAME>";
        if (!fn.default[api]) throw new Error(`Not found function ${api}`);
        const res = await fn.default[api](APIObject(), ...params);
        win.webContents.send("api.<NAMESPACE>.<APINAME>", { code: 200, data: res });
    } catch (err) {
        win.webContents.send("api.<NAMESPACE>.<APINAME>", { code: 404, data: err });
    }
});"""
        res = []
        for api in fnlist:
            tmp = template.replace("<NAMESPACE>", namespace)
            tmp = tmp.replace("<APINAME>", api)
            res.append(tmp)
        return "\n".join(res)

class _Annotator:
    def __init__(self):
        self.definition = Definition()
        self.injection = Injection()
        self.api = API()

Model = _Annotator()