pushing a commit automatically starts a workflow on github ("Actions" tab)



to build on buildouer (defunt, libs ot included)

$ time buildozer android debug deploy run

copy file to www

$ f=`ls -t1 bin/ | head -1` scp bin/$f root@lutolf.vserver.nimag.net:/var/www/html/mtag/


to use ADB:

adb shell dumpsys package | grep -i ' + package.name + ' | grep Activity
adb shell logcat dev.engrenage.meta_tagger/org.kivy.android.PythonActivity |grep python


