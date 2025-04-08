
![Artillery callculator](https://github.com/qSlider/Arma-3-Artillery-Callculator/blob/master/image2.png)

# Artillery Calculator for Arma 3

## How to use?
You may set positions either by manual input or via points on the map.  
If you use **Air Friction**, do not forget to enter **Meteo** or you will get bad results.  
You may **save** and **delete** results; they are also saved if you close the program.

---

## How to import a map from Arma 3?

### Required tools:
- [ocap-renderterrain](https://github.com/indig0fox/ocap-renderterrain)
- [Beowulf's ArmaTerrainExport](https://ocap2.notion.site/Setting-up-Beowulf-s-ArmaTerrainExport-ec09c6d769c549c2986dcd688f6b41b7)

### Steps:
1. Copy `bate_x64.dll` to the directory with the game.
2. Perform the steps with **diag version enabled**.
3. In the **debug console**, enter the following script to export the map to SVG format:
    ```sqf
    diag_exportTerrainSVG ["C:\Zagorsk.svg", true, true, true, false, true, true];
    ```
4. Then enter this script to export terrain height data in 10-meter increments:
    ```sqf
    [] spawn { 
        if (!canSuspend) exitWith { "Must be spawned!" }; 

        "bate" callExtension ["new", []]; 
        private _worldsize = worldSize; 
        startLoadingScreen ["Exporting..."]; 

        _divisor = 10; // Step size: 10 meters

        systemChat format["Cell size: %1", _divisor]; 
        systemChat format["Width/Height: %1", ((worldSize / _divisor) + 1)]; 

        for "_x" from 0 to _worldsize step _divisor do { 
            for "_y" from 0 to _worldsize step _divisor do { 
                "bate" callExtension ["data", [_x, _y, getTerrainHeightASL [_x, _y]]]; 
            }; 
            progressLoadingScreen (_x / _worldsize); 
        }; 
        "bate" callExtension ["end", []]; 
        endLoadingScreen; 
    };
    ```
5. The height data file is usually saved in `C:\arma3\terrain` and renamed to match the map name.
6. Convert the `.svg` map to `.png` using tools such as:
   - **GIMP 2**
   - **ImageMagick**
7. Place the `.svg` file in the `map/img` folder.  
   Place the height data file in the `map/data` folder.

---

## How to add new artillery systems to the calculator?

1. Open `config.json`.
2. Copy an already existing system and enter the following data:

```json
{
    "name": "2B11 Podnos",
    "k_base": -6e-05,
    "shells": [
        {
            "name": "HE",
            "charges": {
                "Charge 0": speed // Found in the ACE table by hovering over the charge
            }
        }
    ]
}
