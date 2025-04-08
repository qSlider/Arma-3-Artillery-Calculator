
![Artillery callculator](https://github.com/qSlider/Arma-3-Artillery-Callculator/blob/master/image2.png)

How to use?
You may set positions either by manual input or via points on the map.
If you use Air Friction do not forget to enter Meteo or you will get bad results.
You may save and delete results, also they are saved if you close the program.

How to import a map from ARMA 3?
1.https://github.com/indig0fox/ocap-renderterrain and https://ocap2.notion.site/Setting-up-Beowulf-s-ArmaTerrainExport-ec09c6d769c549c2986dcd688f6b41b7
copy bate_x64.dll to the directory with the game.
2.Do the steps with diag version enabled
3.In the debug console enter this script diag_exportTerrainSVG ["C:\Zagorsk.svg", true, true, true, false, true, true];.It imports the map into svg format.
4.In the debug console, enter this script.
[] spawn { 
    if (!canSuspend) exitWith { "Must be spawned!" }; 
 
    "bate" callExtension ["new", []]; 
    private _worldsize = worldSize; 
    startLoadingScreen ["Exporting..."]; 
 
    // Задаем шаг 10 метров 
    _divisor = 10; 
 
    systemChat format["Cell size: %1", _divisor]; 
    systemChat format["Width/Height: %1", ((worldSize / _divisor) + 1)]; 
 
    for "_x" from 0 to _worldsize step _divisor do { 
        for "_y" from 0 to _worldsize step _divisor do { 
            // Сохранение данных с точностью 
            "bate" callExtension ["data", [_x, _y, getTerrainHeightASL [_x, _y]]]; 
        }; 
        progressLoadingScreen (_x / _worldsize); 
    }; 
    "bate" callExtension ["end", []]; 
    endLoadingScreen; 
}; 


it allows you to import heights in 10 meter increments, it is usually saved in this directory C:\arma3\terrain and renamed to match the map name.
5.We can by default throw in the folder map/img .svg file, but it is not desirable to do it is better to translate it into png using tools such as:
GIMP 2
ImagineMagick
6.The file with heights throw to the folder map/data.
How to add new systems to the calculator?
1.Open config.json
2.Copy an already existing system and enter the following data:
“name": ‘2B11 Podnos’ - name of the system
“k_base": -6e-05 - if you use Air Friction on games you must fill it in, you can find out in the ACE table by pointing at the charge.
“name": ”HE” - shell names
“Charge 0": - speed of each charge, you can also find out in the ACE table by hovering over the charge.
