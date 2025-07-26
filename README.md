<!-- markdownlint-disable MD033 MD041 -->

# MaaGF1_Test

---

> **本仓库基于 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 项目模板创建**

**MaaGF1_Test** 是用于**少女前线Steam版本**自动化测试的仓库。由于是新生项目，可能存在：

- 界面简陋
- 功能单一
- 结构混乱
- 逻辑复杂
- 可读性差

⚠️ **账号风险警告** ⚠️  
少女前线官方声明：使用脚本存在封号风险  
**账号安全自行判断，该项目不承担任何后果**

---

## **⚠️请在更新到最新发行版并阅读完以下说明、看完相关[使用手册](https://github.com/LeonNagant/MaaGF1_Test/tree/main/manual)  后再使用脚本！否则脚本可能无法正常运行！**

## **⚠️请在更新到最新发行版并阅读完以下说明、看完相关[使用手册](https://github.com/LeonNagant/MaaGF1_Test/tree/main/manual)  后再使用脚本！否则脚本可能无法正常运行！**

## **⚠️请在更新到最新发行版并阅读完以下说明、看完相关[使用手册](https://github.com/LeonNagant/MaaGF1_Test/tree/main/manual)  后再使用脚本！否则脚本可能无法正常运行！**

**由于开发和维护人员数量和精力有限，请在反馈bug前检查资源版本、阅读使用手册，若确认该bug是可复现的，请将软件根目录下debug/文件夹中的 *maa.log*作为附件上传，视频和图片也会提高我们查错的速度。**

---

## 📜 脚本说明

### 🖥️ 分辨率配置

#### 当前支持

- **主开发分辨率**：1680×1050
- **未来更新计划**：1280×800（开发中）

#### 分辨率 Q&A

**Q：为什么选用1680×1050分辨率？**  
A：该分辨率长宽比可点击所有支持地图的关键点位，同时高分辨率确保识别精度 ~~（绝不是因为LeonNagant偷懒不做全适配）~~

**Q：我的显示器不支持此分辨率怎么办？**  
A：少女前线会根据显示器自动适配可选分辨率。若使用相近分辨率（如1600×1024），脚本可能仍可运行，但需要手动校准初始位置（详见各功能使用手册中的校准说明）

**Q：我的显示器是1920×1080的，使用1680×1050会导致任务栏遮挡游戏窗口该怎么办？**  
A：可以设置任务栏为**自动隐藏**/**垂直任务栏** ~~，LeonNagant偷懒不做全适配，自己也在将就用~~

---

### ⚠️ 重要注意事项

#### 1. 鼠标占用问题

- **现象**：执行时系统鼠标被程序抢走点击少女前线窗口~~丹德莱和你抢鼠标~~
- **暂时解决方案**：

  ```快捷键
  Win + ↓（连续按至少女前线窗口最小化）
  ```

- *诚征技术方案*：欢迎提供后台点击实现方案

#### 2. 必读文档

- [使用手册全集](https://github.com/LeonNagant/MaaGF1_Test/tree/main/manual)  
```! 未阅读手册直接使用可能导致脚本异常，请在按照使用手册排查问题后，确认你是在最新的发行版遇到bug再进行反馈```

#### 3. 普通用户使用指南

1. 下载最新[发行版](https://github.com/LeonNagant/MaaGF1_Test/releases/tag/release)  
   `MaaGF1-GUI-win-x86_64-.zip`
2. 解压文件
3. 运行 `MFAAvalonia.exe`
4. 选择「少女前线」窗口
5. 选择要执行的脚本，循环次数保持为"1"不变即可（未来可能会加入循环次数选择）
6. 点击开始运行

---

## 🚀 已支持功能

- ## 升级

### ▶️ 8-1N双打手炸狗

- [8-1N双打手炸狗使用手册](https://github.com/LeonNagant/MaaGF1_Test/blob/main/manual/8-1N%E5%8F%8C%E6%89%93%E6%89%8B%E7%82%B8%E7%8B%97%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C.md)

### ▶️ 13-4双打手拖尸

- [13-4双打手拖尸使用手册](https://github.com/LeonNagant/MaaGF1_Test/blob/main/manual/13-4%E5%8F%8C%E6%89%93%E6%89%8B%E6%8B%96%E5%B0%B8%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C.md)

- ## 打捞

### ▶️ MP41抽薪打捞————feat.[Ethan Lee](https://github.com/hake971920)

- [MP41抽薪打捞使用手册](https://github.com/LeonNagant/MaaGF1_Test/blob/main/manual/MP41%E6%8A%BD%E8%96%AA%E6%89%93%E6%8D%9E%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C.md)

- ## 宿舍功能

### ▶️ 兵棋自动挂机

- [兵棋自动挂机使用手册](https://github.com/LeonNagant/MaaGF1_Test/blob/main/manual/%E5%85%B5%E6%A3%8B%E8%87%AA%E5%8A%A8%E6%8C%82%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C.md)

### ▶️ 宿舍自动点赞

### ▶️ 点击宿舍里的爱心❤图标

- ## 其他

### ▶️ 自动打灰奖励关（1680x1050或者1280x800多分辨率支持!） ——feat.[do_e](https://github.com/isla23)

- [操作手册](https://github.com/LeonNagant/MaaGF1_Test/blob/main/manual/%E8%87%AA%E5%8A%A8%E6%89%93%E7%81%B0%E5%A5%96%E5%8A%B1%E5%85%B3%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C.md)

### ▶️ 裂变链接捡垃圾 **（WIP *目前只适用于1280x720*）** ——feat.[Talulah-x](https://github.com/Talulah-x)

-

## 🔧 更多功能开发中

---

## ❓ 反馈渠道

[提交 Issue](https://github.com/LeonNagant/MaaGF1_Test/issues)

QQ群：*720731834*

---

## 📄免责声明与许可

### **该项目仅供学习交流使用，不对账号风险负责，是否使用请用户自行判断。**

该项目其余声明与许可均继承于[MaaFramework](https://github.com/MaaXYZ/MaaFramework)，使用该程序默认**已完全阅读并同意**该项目以及MaaFramework的所有声明与许可。

---

## 🙏 鸣谢

本项目由 **[MaaFramework](https://github.com/MaaXYZ/MaaFramework)** 强力驱动！

感谢参与了该项目开发、测试的所有开发者和用户！
