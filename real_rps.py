"""Rock paper scissors using the camera, the hand recognison is med using a ai"""

import time
import random
import mediapipe as mp
import cv2

class HandDetection():
    """Useful functions to detemine hand information from picture"""

    def __init__(self, mode=False, max_hands=2, min_detection_con=0.5, min_track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.min_detection_con = min_detection_con
        self.min_track_con = min_track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode,
                                         self.max_hands,
                                         self.min_detection_con,
                                         self.min_track_con)
        self.mp_draw = mp.solutions.drawing_utils

        self.lm_results = None

    def find_hands(self, img, draw=True):
        """Finds hands esentioal locations"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.lm_results = self.hands.process(img_rgb)

        if self.lm_results.multi_hand_landmarks:
            for hand_lms in self.lm_results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)

        return img

    def find_lm_positions(self, img, hand_num=0):
        """Finds the psoition of the hands landmarks"""
        lm_list = []
        if self.lm_results.multi_hand_landmarks:
            my_hand = self.lm_results.multi_hand_landmarks[hand_num]

            for _, landmark in enumerate(my_hand.landmark):
                height, width, _ = img.shape
                cur_x, cur_y = int(landmark.x*width), int(landmark.y*height)
                pos = (cur_x, cur_y)
                lm_list.append(pos)

        return lm_list

    def get_avg_hand_pos(self, img, lm_lst, draw = True):
        """Get the acerage postioin of the landmarks"""
        if self.lm_results.multi_hand_landmarks:
            total_x = 0
            total_y = 0
            total = 0
            for landmark in lm_lst:
                total_x += landmark[0]
                total_y += landmark[1]
                total += 1

            pos_x = total_x/total
            pos_y = total_y/total

            avg_pos = (int(pos_x), int(pos_y))

            if draw:
                self.draw_circle(img, avg_pos, 15, (255, 0, 255))

            return avg_pos

        return None

    def get_finger_states(self, lm_lst):
        """Gets the curent state for each finger"""
        thumb_open = False
        first_finger_open = True
        second_finger_open = True
        third_finger_open = True
        fourth_finger_open = True

        pseudo_fix_key_point = lm_lst[3][1]
        if lm_lst[4][1] < pseudo_fix_key_point:
            thumb_open = True

        pseudo_fix_key_point = lm_lst[6][0]
        if lm_lst[7][0] < pseudo_fix_key_point and lm_lst[8][0] < pseudo_fix_key_point:
            first_finger_open = False

        pseudo_fix_key_point = lm_lst[10][0]
        if lm_lst[11][0] < pseudo_fix_key_point and lm_lst[12][0] < pseudo_fix_key_point:
            second_finger_open = False

        pseudo_fix_key_point = lm_lst[14][0]
        if lm_lst[15][0] < pseudo_fix_key_point and lm_lst[16][0] < pseudo_fix_key_point:
            third_finger_open = False

        pseudo_fix_key_point = lm_lst[18][0]
        if lm_lst[19][0] < pseudo_fix_key_point and lm_lst[20][0] < pseudo_fix_key_point:
            fourth_finger_open = False

        dic = {"Thumb" : thumb_open,
            "Index" : first_finger_open,
            "Middle" : second_finger_open,
            "Ring" : third_finger_open,
            "Pinky" : fourth_finger_open}

        return dic

    def draw_circle(self, img, pos, radius, color = (0, 126, 126)):
        """Draws circle at given position"""
        cv2.circle(img, pos, radius, color, cv2.FILLED)

class RockPaperScissor():
    """Game ruls and updates to play rock paper scissor"""
    def __init__(self):
        self.time = 0
        self.print1 = True
        self.print2 = True
        self.over = False
        self.count = 0

    def current_hand(self, finger_states_dic):
        """Checks that symbol hand is doing"""
        if (not finger_states_dic["Thumb"] and
            not finger_states_dic["Index"] and
            not finger_states_dic["Middle"] and
            not finger_states_dic["Ring"] and
            not finger_states_dic["Pinky"]):
            return "ROCK"

        if (finger_states_dic["Thumb"] and
            finger_states_dic["Index"] and
            finger_states_dic["Middle"] and
            finger_states_dic["Ring"] and
            finger_states_dic["Pinky"]):
            return "PAPER"

        if (not finger_states_dic["Thumb"] and
            finger_states_dic["Index"] and
            finger_states_dic["Middle"] and
            not finger_states_dic["Ring"] and
            not finger_states_dic["Pinky"]):
            return "SCISSOR"

        if (finger_states_dic["Thumb"] and
            not finger_states_dic["Index"] and
            finger_states_dic["Middle"] and
            not finger_states_dic["Ring"] and
            not finger_states_dic["Pinky"]):
            return "FUCK YOU"

        return None

    def count_down(self, delta_time, real_deal = True):
        """Does the count down for rps, eather by checking the position of the hand
           or by counting in time"""

        if real_deal:
            if self.count == 1:
                print("Rock!")
                return False
            elif self.count == 2:
                print("Paper!")
                return False
            elif self.count == 3:
                print("Scissor!")
                print("")
                time.sleep(0.1)
                return True
        else:
            self.time += delta_time
            if self.time >= 1 and self.time < 1.7 and self.print1:
                self.print1 = False
                print("Rock!")
                return False
            elif self.time >= 1.7 and self.time < 2.4 and self.print2:
                self.print1 = True
                self.print2 = False
                print("Paper!")
                return False
            elif self.time >= 2.4:
                self.print1 = False
                self.print2 = False
                print("Scissor!")
                print("")
                self.time = 0
                time.sleep(0.1)
                return True
            else:
                return False

    def up_down_count(self, img, avg_pos):
        """Checking if the hand is moving from the lower area of the scrren
           to the upper area"""
        middle_horizontal = (2*img.shape[1])/5
        if avg_pos:
            if avg_pos[1] < middle_horizontal:
                self.over = True

            if self.over and avg_pos[1] > middle_horizontal:
                self.over = False
                return 1

        return 0

    def rps(self, img, lm_lst, avg_pos, finger_status, delta_time):
        """General rules for rps"""
        self.count += self.up_down_count(img, avg_pos)
        if self.count_down(delta_time):
            if len(lm_lst) != 0:
                state_of_fingers = finger_status
                hand = self.current_hand(state_of_fingers)
                options = ["ROCK", "PAPER", "SCISSOR"]

                ai_option = options[random.randint(0, len(options)-1)]

                if ai_option == hand:
                    return f"Eaven! Booth choose {hand}"

                if ((ai_option == "ROCK" and hand == "PAPER") or
                    (ai_option == "PAPER" and hand == "SCISSOR") or
                    (ai_option == "SCISSOR" and hand == "ROCK")):
                    return f"You Win! Computer: {ai_option} You: {hand}"

                if ((hand == "ROCK" and ai_option == "PAPER") or
                    (hand == "PAPER" and ai_option == "SCISSOR") or
                    (hand == "SCISSOR" and ai_option == "ROCK")):
                    return f"You Lose! Computer: {ai_option} You: {hand}"

                if hand == "FUCK YOU":
                    return "Fyck you too!"

                return "Error: Hand does not match rock, paper och scissor"

        return None

def main():
    """Main function for the program"""
    cap = cv2.VideoCapture(0)

    detector = HandDetection()

    game = RockPaperScissor()

    run = True

    p_time = time.time()+0.1
    c_time = 0

    while run:
        c_time = time.time()
        delta_time = c_time-p_time
        fps = 1/(delta_time)

        _, img = cap.read()
        img = detector.find_hands(img, False)
        lm_lst = detector.find_lm_positions(img)
        if len(lm_lst) != 0:
            avg_pos = detector.get_avg_hand_pos(img, lm_lst, True)
            finger_status = detector.get_finger_states(lm_lst)
            result = game.rps(img, lm_lst, avg_pos, finger_status, delta_time)
            if result:
                print(result)
                run = False


        img_flipped = cv2.flip(img, 1)
        cv2.putText(img_flipped,
                    str(int(fps)), (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
        cv2.imshow("Image", img_flipped)
        cv2.waitKey(1)

        p_time = c_time



if __name__ == "__main__":
    main()
