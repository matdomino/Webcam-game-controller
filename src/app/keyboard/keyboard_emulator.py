import queue
from collections import deque
from ..gestures.joint_angle import calculate_joint_angle
from ..gestures.hand_gestures import calculate_gesture
from ..gestures.body_gestures import is_left_hand_active, is_leaning
from .keyboard_input import hold_key, release_key, single_key_press
from pynput.keyboard import Controller, Key

def left_hand_single_action(gesture, last_hand_gesture, k_config, k_controller) -> str | None:
    """
    Clears a specified number of elements from the queue.

        Parameters:
            - queue(queue.Queue): Specified queue from which elements will be removed.
            - amount(int): number of elements to remove.

        Returns:
            - None
    """

    if gesture == last_hand_gesture:
        return

    match gesture:
        case "four_fingers_up":
            single_key_press(k_config['l-four-up'], k_controller)
        case "index_finger_up":
            single_key_press(k_config['l-index-up'], k_controller)
        case "peace_sign":
            single_key_press(k_config['l-peace'], k_controller)
        case "three_fingers_up":
            single_key_press(k_config['l-three-up'], k_controller)
        case _:
            return

def walk(body_landmarks, walking_history_queue, walking_queue_length, k_config, k_controller) -> None:
    """
    Emulates a walking function for half a second when the knee angle is less than 110 degrees.

        Parameters:
            - body_landmarks(RepeatedCompositeFieldContainer): Predicted body landmarks.
            - walking_history_queue(deque): Queue used to emulate walking function for half a second.
            - walking_queue_length(int): Length of the walking queue, based on camera's fps.
            - k_config(dict): Keybinds configuration.
            - k_controller(Controller): Keyboard controller (Pynput).

        Returns:
            - None
    """

    if (calculate_joint_angle(body_landmarks[26], body_landmarks[24], body_landmarks[12]) < 110 or
        calculate_joint_angle(body_landmarks[25], body_landmarks[23], body_landmarks[11]) < 110):

        walking_history_queue.extend([1] * walking_queue_length)
        hold_key(k_config['Walk'], k_controller)

    try:
        walking_history_queue.popleft()

    except IndexError:
        release_key(k_config['Walk'], k_controller)

# ZMIENIC PO DODANIU MAPOWANIA KONFIGU
def jump(body_landmarks, k_config, k_controller) -> None:
    """
    Emulates a jumping function when the knee angle of both legs is less than 90 degrees.

        Parameters:
            - body_landmarks(RepeatedCompositeFieldContainer): Predicted body landmarks.
            - k_config(dict): Keybinds configuration.
            - k_controller(Controller): Keyboard controller (Pynput).

        Returns:
            - None
    """

    if (calculate_joint_angle(body_landmarks[26], body_landmarks[24], body_landmarks[12]) < 90 and
        calculate_joint_angle(body_landmarks[25], body_landmarks[23], body_landmarks[11]) < 90):
        if k_config["Jump"] == "space":
            single_key_press(Key.space, k_controller)
            return

        single_key_press(k_config["Jump"], k_controller)

# ZMIENIC PO DODANIU MAPOWANIA KONFIGU
def sprint(hand_gesture, is_sprinting, k_config, k_controller) -> bool:
    """
    Emulates a sprinting function when the left hand gesture is "open_palm".

        Parameters:
            - hand_gesture(str): Prediction od the left hand gesture.
            - is_sprinting(bool): Previous iteration's sprinting status.
            - k_config(dict): Keybinds configuration.
            - k_controller(Controller): Keyboard controller (Pynput).

        Returns:
            - None
    """

    if hand_gesture == "open_palm":
        if is_sprinting is False:
            hold_key(Key.ctrl, k_controller)

        return True

    if is_sprinting is True:
        release_key(Key.ctrl, k_controller)

    return False

def walk_sideways(body_landmarks, was_leaning, k_config, k_controller) -> str | bool:
    """
    Emulates a walking sideways function when the head is leaning left or right beyond the hip.

        Parameters:
            - body_landmarks(RepeatedCompositeFieldContainer): Predicted body landmarks.
            - was_leaning(str | bool): The previous leaning status from the last iteration.
            - k_config(dict): Keybinds configuration.
            - k_controller(Controller): Keyboard controller (Pynput).

        Returns:
            - None
    """

    leaning_status = is_leaning(body_landmarks[24], body_landmarks[23], body_landmarks[0])

    if not leaning_status:
        return False

    if leaning_status == was_leaning:
        return was_leaning

    match leaning_status:
        case "right":
            if was_leaning == "left":
                release_key(k_config["Go left"], k_controller)
            hold_key(k_config["Go right"], k_controller)
            return "right"
        case "left":
            if was_leaning == "right":
                release_key(k_config["Go right"], k_controller)
            hold_key(k_config["Go left"], k_controller)
            return "left"

def run_keyboard_emulation(keyboard_landmarks_queue, k_config, camera_fps, exit_event) -> None:
    """
    Main process for the emulation thread, responsible for running keyboard emulation.

        Parameters:
            - keyboard_landmarks_queue(queue.Queue): Queue for body landmarks.
            - k_config(dict): Keybinds configuration.
            - camera_fps(float): Camera's fps.
            - exit_event(threading.Event): Exit event flag to stop the aplication.

        Returns:
            - None
    """

    # DODAC TUTAJ FUNKCJE DO MAPOWANIA CONFIGU, ZEBY JESLI JEST ZNAK SPACJALNY ZMIENILA GO NA OBIEKT KEY

    k_controller = Controller()
    last_hand_gesture = None
    is_sprinting = False
    is_leaning = False
    # Queue for a 1/2 second duration, depends on camera's FPS.
    walking_queue_length = int(camera_fps/2)
    walking_history_queue = deque(maxlen=walking_queue_length)

    while not exit_event.is_set():
        try:
            left_hand, body = keyboard_landmarks_queue.get(timeout=1)

            hand_gesture = calculate_gesture(left_hand)

            if is_left_hand_active(body[15], body[23], body[0]):
                left_hand_single_action(hand_gesture, last_hand_gesture, k_config, k_controller)

                is_sprinting = sprint(hand_gesture, is_sprinting, k_config, k_controller)

            is_leaning = walk_sideways(body, is_leaning, k_config, k_controller)

            walk(body, walking_history_queue, walking_queue_length, k_config, k_controller)

            jump(body, k_config, k_controller)

            last_hand_gesture = hand_gesture

        except queue.Empty:
            pass
