"""
BoundingBoxManager class for managing bounding box operations.
"""

import cv2


class BoundingBoxManager:
    def __init__(self):
        self.boxes = []  # List of (box_coordinates_tuple, box_id_string, class_label_string)
        self.selected_box_index = -1
        self.base_line_width = 2
        self.selected_line_width = 3
        self.base_circle_radius = 5
        self.min_line_width = 1
        self.min_circle_radius = 3
        self.max_line_width = 5
        self.max_circle_radius = 10

    def draw_boxes(self, cv_image, drawing=False, start_point=None, end_point=None):
        """
        Draws all stored bounding boxes onto the display image.
        The currently selected box is highlighted with a different color and corner circles.
        """
        if cv_image is None:
            return cv_image.copy()

        display_image = cv_image.copy()

        for idx, (box, _, _) in enumerate(self.boxes):
            x1, y1, x2, y2 = map(int, box)
            if idx == self.selected_box_index:
                color = (255, 255, 0)  # Yellow for selected box
                thickness = self.get_adaptive_line_width(cv_image, is_selected=True)
                circle_radius = self.get_adaptive_circle_radius(cv_image)
                # Draw circles at corners with adaptive radius for the selected box
                cv2.circle(display_image, (x1, y1), circle_radius, color, -1)
                cv2.circle(display_image, (x2, y1), circle_radius, color, -1)
                cv2.circle(display_image, (x1, y2), circle_radius, color, -1)
                cv2.circle(display_image, (x2, y2), circle_radius, color, -1)
            else:
                color = (0, 255, 0)  # Green for unselected boxes
                thickness = self.get_adaptive_line_width(cv_image, is_selected=False)
            cv2.rectangle(display_image, (x1, y1), (x2, y2), color, thickness)

        # Draw the rectangle being currently drawn by the user (temporary highlight)
        if drawing and start_point and end_point:
            x1, y1 = start_point
            x2, y2 = end_point
            x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
            thickness = self.get_adaptive_line_width(cv_image, is_selected=True)
            cv2.rectangle(display_image, (x1, y1), (x2, y2), (255, 255, 0), thickness)

        return display_image

    def get_adaptive_line_width(self, cv_image, is_selected=False):
        """
        Calculates an adaptive line width for drawing boxes based on image resolution.
        """
        if cv_image is None:
            return self.selected_line_width if is_selected else self.base_line_width

        height, width = cv_image.shape[:2]
        diagonal = (width**2 + height**2)**0.5

        base_diagonal = 1000

        if is_selected:
            line_width = max(self.min_line_width,
                            min(self.max_line_width,
                               int(self.selected_line_width * diagonal / base_diagonal)))
        else:
            line_width = max(self.min_line_width,
                            min(self.max_line_width,
                               int(self.base_line_width * diagonal / base_diagonal)))

        return line_width

    def get_adaptive_circle_radius(self, cv_image):
        """
        Calculates an adaptive circle radius for corner handles based on image resolution.
        """
        if cv_image is None:
            return self.base_circle_radius

        height, width = cv_image.shape[:2]
        diagonal = (width**2 + height**2)**0.5

        base_diagonal = 1000

        radius = max(self.min_circle_radius,
                    min(self.max_circle_radius,
                        int(self.base_circle_radius * diagonal / base_diagonal)))

        return radius

    def delete_box(self, index_to_delete: int):
        """
        Deletes a box at the specified index.
        """
        if not 0 <= index_to_delete < len(self.boxes):
            return False

        if self.selected_box_index == index_to_delete:
            self.selected_box_index = -1
        elif self.selected_box_index > index_to_delete:
            self.selected_box_index -= 1

        del self.boxes[index_to_delete]
        return True

    def get_box_containing(self, pos):
        """
        Returns the index of the box containing the given position.
        """
        x, y = pos
        for i in reversed(range(len(self.boxes))):
            box, _, _ = self.boxes[i]
            x1, y1, x2, y2 = box
            if x1 < x < x2 and y1 < y < y2:
                return i
        return -1

    def resize_box(self, pos, resize_box_index, resize_edge, img_dimensions):
        """
        Resizes the selected bounding box based on the current mouse position and resize edge.
        """
        if resize_box_index is None:
            return False

        x, y = pos
        i = int(resize_box_index)
        box, box_id, label = self.boxes[i]
        x1_orig, y1_orig, x2_orig, y2_orig = box

        x1, y1, x2, y2 = x1_orig, y1_orig, x2_orig, y2_orig
        img_h, img_w = img_dimensions

        # Adjust coordinates based on the active resize edge
        if resize_edge == 'left':
            x1 = x
        elif resize_edge == 'right':
            x2 = x
        elif resize_edge == 'top':
            y1 = y
        elif resize_edge == 'bottom':
            y2 = y
        elif resize_edge == 'top-left':
            x1 = x
            y1 = y
        elif resize_edge == 'top-right':
            x2 = x
            y1 = y
        elif resize_edge == 'bottom-left':
            x1 = x
            y2 = y
        elif resize_edge == 'bottom-right':
            x2 = x
            y2 = y

        # Ensure coordinates stay within image bounds
        x1 = max(0, min(x1, img_w - 1))
        y1 = max(0, min(y1, img_h - 1))
        x2 = max(0, min(x2, img_w - 1))
        y2 = max(0, min(y2, img_h - 1))

        # Sort coordinates to ensure positive dimensions
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        # Ensure minimal size
        if abs(x2 - x1) < 1:
            x2 = x1 + 1
            if x2 >= img_w:
                x1 = img_w - 2
                x2 = img_w - 1

        if abs(y2 - y1) < 1:
            y2 = y1 + 1
            if y2 >= img_h:
                y1 = img_h - 2
                y2 = img_h - 1

        self.boxes[i] = (x1, y1, x2, y2), box_id, label
        return True

    def convert_to_normalized_center(self, box, img_width, img_height):
        """Convert (x1, y1, x2, y2) to normalized (x_center, y_center, width, height)"""
        x1, y1, x2, y2 = box
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height
        x_center = (x1 + x2) / (2 * img_width)
        y_center = (y1 + y2) / (2 * img_height)
        return x_center, y_center, width, height

    def convert_from_normalized_center(self, norm_box, img_width, img_height):
        """Convert normalized (x_center, y_center, width, height) to (x1, y1, x2, y2)"""
        x_center, y_center, width, height = norm_box
        x1 = int((x_center - width/2) * img_width)
        y1 = int((y_center - height/2) * img_height)
        x2 = int((x_center + width/2) * img_width)
        y2 = int((y_center + height/2) * img_height)
        return x1, y1, x2, y2
