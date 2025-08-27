# BootKernelChanger

**BootKernelChanger** — Приложение для изменения ядра (kernel image) в `boot.img`.  
Нужно для того чтобы заменить стандартное ядро на кастомное или уже патченное ядро, легче чем в консоли команды писать)

---
- Интерфейс на Tkinter
- Выбор `boot.img` и нового ядра (`kernel image`)
- Автоматическая распаковка и сборка `boot.img` с помощью встроенного `magiskboot.exe`
- Показ лога
- `.exe` (Windows)

---
## Скриншоты
![Главное окно](https://i.imgur.com/xToHaRd_d.webp?maxwidth=760&fidelity=grand)  
---

## Использование

1. Запустите `BootKernelChanger.exe`.
2. Выберите ваш текущий `boot.img`.
3. Выберите ядро (`Image`), которое хотите вставить.
4. Нажмите **Собрать**.
5. Сохраните новый `boot.img`.
---
