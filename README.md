# wukongtv
悟空遥控TV for homeassistant


![1](https://github.com/dscao/wukongtv/assets/16587914/f1f712d4-ca48-4221-b549-2c7209d67ca0)



![2](https://github.com/dscao/wukongtv/assets/16587914/c4af9f83-afb2-41dc-a535-4cd403795e1f)



![3](https://github.com/dscao/wukongtv/assets/16587914/2b3c9f90-5bec-49f1-b20a-899ab750a8e5)



![5](https://github.com/dscao/wukongtv/assets/16587914/ba738281-f064-4b0f-866e-f34e490cd423)


投屏播放暂不支持

可用服务：

打开APP
```yaml
service: media_player.select_source
data:
  source: 当贝桌面|com.dangbei1.tvlauncher  #参考ui界面中的信号源,等效于点击信号源
target:
  entity_id: media_player.wukongtv
```
打开app的另一种方式：
```yaml
service: wukongtv.send_open_command
data:
  appid: nl.rogro82.pipup
```
控制命令：code: [tv_connect,tv_up,tv_down,tv_left,tv_right,tv_home,tv_ok,tv_back,tv_volup,tv_voldown,tv_power,tv_menu,tv_0,……,tv_clean,tv_clean_cache,tv_opensetting,tv_childlock,tv_install_dangbeimarket]
```yaml
service: wukongtv.send_control_command
data:
  code: tv_ok
```
控制命令的另一种试：
```yaml
service: button.press
data: {}
target:
  entity_id: button.wukongtv_fan_hui
```

安装app，仅限yaokong.wukongtv.com上的app
```yaml
service: wukongtv.send_install_command
data:
  appurl: >-
    http://yaokong.wukongtv.com/appstore/yaokong.php?p=com.dangbeimarket&source=wukong"  #网址必须是yaokong.wukongtv.com下才能安装，否则提示非法网址。
```

通过pipup弹出小窗口显示消息通知
```yaml
service: wukongtv.send_pipup_command
data:
  mediatype: web
  message: this is the message
  title: title
  httpurl: https://www.baidu.com/
  duration: 20
  titlecolor: red
  titlesize: 24
  messagecolor: white
  messagesize: 16
  backgroundcolor: black
  width: 640
  height: 480
target:
  entity_id: media_player.wukong
```
电视或盒子需要安装好 [pipup](https://github.com/rogro82/PiPup-homey)，并启动进程在后台。

![动画](https://github.com/dscao/wukongtv/assets/16587914/2df88461-1314-44b6-b301-fcf496762758)

