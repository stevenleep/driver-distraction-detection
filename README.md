# Windows 环境准备
#### 安装scoop
https://get.scoop.sh
```ini
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

#### 安装pipx环境
https://pipx.pypa.io/stable/installation/
```ini
scoop install pipx
pipx ensurepath
```

#### 安装poetry
```ini
pipx install poetry
```

## 运行项目
#### 开启虚拟化环境
```ini
# 将.venv放在项目目录中
poetry config virtualenvs.in-project true

# 进入虚拟化环境
poetry env use python3
poetry shell
```

#### 安装依赖
```ini
poetry install
```

#### 运行项目
```ini
flask run
```

## 访问
[Open in browser http://127.0.0.1:26666](http://127.0.0.1:26666)