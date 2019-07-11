import json
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Клавиатура для всего, кроме диагнозов
def default_keyboard(prepare):
    keyboard = VkKeyboard(one_time=True)
    temp_for_long = []
    temp_for_little = []
    for i in range(len(prepare)):

        # если содержимое кнопки выходит за рамки
        if (len(prepare[i]) > 25):
            temp_for_long.append([{
                "action": {
                    "type": "text",
                    "payload": json.dumps(""),
                    "label": prepare[i]
                },
                "color": "primary"
            }])
        else:
            temp_for_little.append({
                "action": {
                    "type": "text",
                    "payload": json.dumps(""),
                    "label": prepare[i]
                },
                "color": "primary"
            })
    if (len(temp_for_long) > 0 and len(temp_for_little) > 0):
        keyboard = {
            "one_time": True,
            "buttons": temp_for_long + [temp_for_little]
        }
    elif (len(temp_for_long) > 0 and len(temp_for_little) < 1):
        keyboard = {
            "one_time": True,
            "buttons": temp_for_long
        }
    elif (len(temp_for_long) < 1 and len(temp_for_little) > 0):
        keyboard = {
            "one_time": True,
            "buttons": [temp_for_little]
        }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard