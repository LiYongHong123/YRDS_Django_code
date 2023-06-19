from pathlib import Path
is_prod = True
HOST = 'http://localhost/'
KEYS={
        1:{},
        2:{},
        3:{""},
        4:{""},
        13: "",
        14: "",
        15: "8db16e8cc8363ed4eb4c14f9520bcc32",
        16: "8db16e8cc8363ed4eb4c14f9520bcc32",
}
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DB = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
}
appid = 'test'
DING_TOKEN = 'b0c1aa7336b03f1052cd4502733494d11e83c14e09be69a0312ea70042564b6c'
privateKey = ''