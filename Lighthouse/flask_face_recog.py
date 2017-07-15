import scipy.misc
from scipy.misc import imread as r
import numpy as np
import dlib
import sys

# load the models -- ??? PRETRAINED ???
face_recognition_model_loc = "./Models/dlib_face_recognition_resnet_model_v1.dat"
face_encoder = dlib.face_recognition_model_v1(face_recognition_model_loc)

# get the face detector
face_detector = dlib.get_frontal_face_detector()

# get the pose predictor
shape_predictor_model_loc = "./Models/shape_predictor_68_face_landmarks.dat"
pose_predictor = dlib.shape_predictor(shape_predictor_model_loc)


def _rect_to_css(rect):
    """
    Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order

    :param rect: a dlib 'rect' object
    :return: a plain tuple representation of the rect in (top, right, bottom, left) order
    """
    return rect.top(), rect.right(), rect.bottom(), rect.left()


def _css_to_rect(css):
    """
    Convert a tuple in (top, right, bottom, left) order to a dlib `rect` object

    :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    :return: a dlib `rect` object
    """
    return dlib.rectangle(css[3], css[0], css[1], css[2])


def _trim_css_to_bounds(css, image_shape):
    """
    Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.

    :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    :param image_shape: numpy shape of the image array
    :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
    """
    return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)


def face_distance(face_encodings, face_to_compare):
    """
    Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
    for each comparison face. The distance tells you how similar the faces are.

    :param faces: List of face encodings to compare
    :param face_to_compare: A face encoding to compare against
    :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
    """
    if len(face_encodings) == 0:
        return np.empty((0))

    return np.linalg.norm(face_encodings - face_to_compare, axis=1)


def load_image_file(filename, mode='RGB'):
    """
    Loads an image file (.jpg, .png, etc) into a numpy array

    :param filename: image file to load
    :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
    :return: image contents as numpy array
    """
    return scipy.misc.imread(filename, mode=mode)


def _raw_face_locations(img, number_of_times_to_upsample=1):
    """
    Returns an array of bounding boxes of human faces in a image

    :param img: An image (as a numpy array)
    :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
    :return: A list of dlib 'rect' objects of found face locations
    """
    return face_detector(img, number_of_times_to_upsample)


def face_locations(img, number_of_times_to_upsample=1):
    """
    Returns an array of bounding boxes of human faces in a image

    :param img: An image (as a numpy array)
    :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
    :return: A list of tuples of found face locations in css (top, right, bottom, left) order
    """
    return [_trim_css_to_bounds(_rect_to_css(face), img.shape) for face in _raw_face_locations(img, number_of_times_to_upsample)]


def _raw_face_landmarks(face_image, face_locations=None):
    if face_locations is None:
        face_locations = _raw_face_locations(face_image)
    else:
        face_locations = [_css_to_rect(face_location) for face_location in face_locations]

    return [pose_predictor(face_image, face_location) for face_location in face_locations]


def face_landmarks(face_image, face_locations=None):
    """
    Given an image, returns a dict of face feature locations (eyes, nose, etc) for each face in the image

    :param face_image: image to search
    :param face_locations: Optionally provide a list of face locations to check.
    :return: A list of dicts of face feature locations (eyes, nose, etc)
    """
    landmarks = _raw_face_landmarks(face_image, face_locations)
    landmarks_as_tuples = [[(p.x, p.y) for p in landmark.parts()] for landmark in landmarks]

    # For a definition of each point index, see https://cdn-images-1.medium.com/max/1600/1*AbEg31EgkbXSQehuNJBlWg.png
    return [{
        "chin": points[0:17],
        "left_eyebrow": points[17:22],
        "right_eyebrow": points[22:27],
        "nose_bridge": points[27:31],
        "nose_tip": points[31:36],
        "left_eye": points[36:42],
        "right_eye": points[42:48],
        "top_lip": points[48:55] + [points[64]] + [points[63]] + [points[62]] + [points[61]] + [points[60]],
        "bottom_lip": points[54:60] + [points[48]] + [points[60]] + [points[67]] + [points[66]] + [points[65]] + [points[64]]
    } for points in landmarks_as_tuples]


def face_encodings(face_image, known_face_locations=None, num_jitters=1):
    """
    Given an image, return the 128-dimension face encoding for each face in the image.

    :param face_image: The image that contains one or more faces
    :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
    :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
    :return: A list of 128-dimentional face encodings (one for each face in the image)
    """
    raw_landmarks = _raw_face_landmarks(face_image, known_face_locations)

    return [np.array(face_encoder.compute_face_descriptor(face_image, raw_landmark_set, num_jitters)) for raw_landmark_set in raw_landmarks]


def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.6):
    """
    Compare a list of face encodings against a candidate encoding to see if they match.

    :param known_face_encodings: A list of known face encodings
    :param face_encoding_to_check: A single face encoding to compare against the list
    :param tolerance: How much distance between faces to consider it a match. Lower is more strict. 0.6 is typical best performance.
    :return: A list of True/False values indicating which known_face_encodings match the face encoding to check
    """
    return list(face_distance(known_face_encodings, face_encoding_to_check) <= tolerance)


def main(raw_image=None):

    # read the test_image as an argument
    if raw_image is None:
        test_image = r(sys.argv[1], mode='RGB')

        print("Image: {}".format(sys.argv[1]))
    else:
        test_image = r(raw_image, mode='RGB')

    # 1. obtain the face encodings
    test_image_face_encodings = face_encodings(test_image)
    print("Found {} faces".format(len(test_image_face_encodings)))

    # data entries are going here
    names = [
        "Dan Sharp",
        "James Arnoldi",
        "Jason Charles",
        "John Simmons",
        "Alan Spohn",
        "Parul Luthra",
        "Mike Stedman",
        "Suman Biswas",
        "Tyler Zupan"
    ]

    # read the known images - data warehouse
    parul = r("./Mugshots/Parul Luthra.jpg", mode='RGB')
    alan = r("./Mugshots/Alan Spohn.jpg", mode='RGB')
    dan = r("./Mugshots/Dan Sharp.jpg", mode='RGB')
    james = r("./Mugshots/James Arnoldi.jpg", mode='RGB')
    jason = r("./Mugshots/Jason Charles.jpg", mode='RGB')
    john = r("./Mugshots/John Simmons.jpg", mode='RGB')
    mike = r("./Mugshots/Mike Stedman.jpg", mode='RGB')
    suman = r("./Mugshots/Suman Biswas.jpg", mode='RGB')
    tyler = r("./Mugshots/Tyler Zupan.jpg", mode='RGB')

    # encode the images
    parul_enc = face_encodings(parul)[0]
    alan_enc = face_encodings(alan)[0]
    dan_enc = face_encodings(dan)[0]
    james_enc = face_encodings(james)[0]
    jason_enc = face_encodings(jason)[0]
    john_enc = face_encodings(john)[0]
    mike_enc = face_encodings(mike)[0]
    suman_enc = face_encodings(suman)[0]
    tyler_enc = face_encodings(tyler)[0]

    # database of encoded mugshots
    known_images = [
        dan_enc,
        james_enc,
        jason_enc,
        john_enc,
        alan_enc,
        parul_enc,
        mike_enc,
        suman_enc,
        tyler_enc
    ]

    # for every face found on the photo, run the comparison
    for i, enc in enumerate(test_image_face_encodings):

        results = compare_faces(known_images, enc)

        if True in results:
            print("Match Found at index: {}".format(i))
            print(names[results.index(True)])

    return 0




