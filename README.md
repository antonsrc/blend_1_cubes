# main.py - точка входа
Основной скрипт. Результаты работы смотрите ниже.

# 2 пути запуска скрипта:
1. В командной строке прописать:  
```blender --background --python main.py``` (где blender - исполняемый файл Blender).
2. В Blender открыть файл start.blend и нажать Run Script (Alt + P).

# Настройки в main.py
Переменной ```PATH_OUT``` задаем путь куда будут сохраняться изображения или анимация.  
Переменными ```OBJ_``` и ```NUM_OBJS``` задаем тип объекта, и его количество соответственно.  
Если переменная ```ANIM = False``` то на выходе получим набор изображений, если ```True``` то получим анимацию.


# Требования
Blender 2.91

# demos (snaps)
![](https://github.com/antonsrc/0_in_the_postman_s_bag/blob/main/out/10_133.jpg?raw=true)
![](https://github.com/antonsrc/0_in_the_postman_s_bag/blob/main/out/3_495.jpg?raw=true)
![](https://github.com/antonsrc/0_in_the_postman_s_bag/blob/main/out/9_389.jpg?raw=true)
