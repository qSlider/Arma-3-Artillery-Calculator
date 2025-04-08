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


Як імпортувати карту з ARMA 3?
1.https://github.com/indig0fox/ocap-renderterrain і https://ocap2.notion.site/Setting-up-Beowulf-s-ArmaTerrainExport-ec09c6d769c549c2986dcd688f6b41b7
bate_x64.dll копіюємо в директорію з грою.
2. робимо кроки з увімкненням diag версії.
3. в консоль налагодження вводимо цей скрипт diag_exportTerrainSVG ["C:\Zagorsk.svg", true, true, true, false, true, true];. він імпортує карту в svg формат.
4.У консоль налагодження вводимо цей скрипт
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

він дає змогу імпортувати висоти з кроком у 10 метрів, зберігається він зазвичай у цій директорії C:\arma3\terrain і перейменовуємо під назви карти.
5 Ми можемо за дефолтом закинути в папку map/img .svg файл, але це робити не бажано, а краще перевести його в png за допомогою таких інструментів як:
GIMP 2
ImagineMagick
6.Файл із висотами перекидаємо в папку map/data.
Як додати нові системи в калькулятор?
1. відкрити config.json
2 Скопіювати вже наявну систему і вписати такі дані:
«name": “2B11 Podnos” - назва системи
«k_base": -6e-05 - якщо ви використовуєте Air Friction на іграх, обов'язково потрібно заповнити, дізнатися можна в таблиці ACE, навівшись на заряд
«name": »HE» - назви снаряда
«Charge 0": - швидкість кожного заряду, можна так само дізнатися в таблиці ACE навівшись на заряд


Как импортировать карту из ARMA 3?
1.https://github.com/indig0fox/ocap-renderterrain и https://ocap2.notion.site/Setting-up-Beowulf-s-ArmaTerrainExport-ec09c6d769c549c2986dcd688f6b41b7
bate_x64.dll копируем в директорию с игрой.
2.Делаем шаги с включением diag верссии
3.В консоль отладки вводим этот скрипт diag_exportTerrainSVG ["C:\Zagorsk.svg", true, true, true, false, true, true];.Он импортирует карту в svg формат.
4.В консоль отладки вводим этот скрипт
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

он позволяет импортировать высоты с шагом в 10 метров , сохраняется он обычно в этой директории C:\arma3\terrain и переименовываем под названия карты
5.Мы можем по дефолту закинуть в папку map/img .svg файл, но это делать не желательно лучше перевести его в png с помощью таких инструментов как:
GIMP 2
ImagineMagick
6.Файл с высотами перекидываем в папку map/data.
Как добавить новые системы в калькулятор?
1.Открыть config.json
2.Скопировать уже существующую систему и вписать такие данные:
"name": "2B11 Podnos" - название системы
"k_base": -6e-05 - если вы используете Air Friction на играх обьязательно нужно заполнить , узнать можно в таблице ACE наведясь на заряд
"name": "HE" - названия снаряда
"Charge 0": - скорость каждого заряда, можно так же узнать в таблице ACE наведясь на заряд
