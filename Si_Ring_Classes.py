from sklearn.neighbors import NearestNeighbors
import math
import numpy
import matplotlib

from skimage import filters
from skimage import morphology
from skimage import measure
from scipy import ndimage as ndi
from skimage import draw
from sklearn.neighbors import NearestNeighbors




def get_distance(pt1, pt2):
    """ Finds the distance between two points. """
    x1 = pt1[0]
    y1 = pt1[1]
    x2 = pt2[0]
    y2 = pt2[1]
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1 / 2)


class Si:
    """ Contains the location of the Si atom, as well as each of the
        three rings surrounding it. Objects do not automatically calculate
        their locations if you do not tell them to. NOTE: The main
        functionality is done in nanometers.  Pixel locations are held on to so
        they can be easy to grab, but, if you start calling complex methods
        with pixel dimensions, you're going to have a bad time. """

    """ Public Methods """

    def __init__(self, x, y, z, unit):
        """ Constructor """
        if unit == "nm":
            self._nm_location = [x, y, z]
            self._pixel_location = [0, 0, 0]
        else:
            self._pixel_location = [x, y, z]
            self._nm_location = [0, 0, 0]
        self._rings = []
        self._d1 = 0
        self._d2 = 0
        self._d3 = 0

    def _findClosestThree(self, ring_list, x_max, y_max, edge_buffer):
        if self.is_edge(x_max, y_max, edge_buffer):
            return

        ring_pos = []

        for ring in ring_list:
            ring_pos.append(ring.get_nm_location())

        nearest = NearestNeighbors(n_neighbors=3, algorithm='ball_tree').fit(ring_pos)
        dist, ind = nearest.kneighbors([self.get_nm_location()])
        for i in range(len(ind[0])):
            self._rings.append(ring_list[ind[0][i]])

    def find_rings(self, ring_list, x_max, y_max, edge_buffer):
        """ Finds the three rings bordering this Si atom, and stores
            them in self._rings.
        self._findFirst(ring_list, x_max, y_max, edge_buffer)
        print("1st ring found!")
        if (len(self.get_rings()) == 1):
            self._findSecond(ring_list, x_max, y_max, edge_buffer)
        if (len(self.get_rings()) == 2):
            self._findThird(ring_list, x_max, y_max, edge_buffer)
        print("size: ", len(self._rings))"""
        self._findClosestThree(ring_list, x_max, y_max, edge_buffer)

    def get_nm_location(self):
        """ Returns the location in (x, y, z) form. Units are nm. """
        return self._nm_location

    def get_pix_location(self):
        """ Returns the location in (x, y, z) form. Units are Pixels"""
        return self._location

    def get_rings(self):
        """ Returns the list of rings bordering the atom. """
        return self._rings

    def is_edge(self, max_x, max_y, edge_buffer):
        """ Determines if this Si atom is on the edge of the image
            returns true if so, false otherwise. """
        x = self.get_nm_location()[0]
        y = self.get_nm_location()[1]
        d = edge_buffer
        return x < d or x > max_x - d or y < d or y > max_y - d

    """ Private Methods """

    def _findFirst(self, ring_list, x_max, y_max, edge_buffer):
        """ Finds the closest ring center to the atom. If there are
            equidistant centers, puts all into self._rings. """
        # Excludes any Si atoms that are included as an edge case
        if self.is_edge(x_max, y_max, edge_buffer):
            return

        # Sets an arbitrary number as the first distance. This number
        # is used because it will be bigger than any distance calculated.
        distance = 100000000000000000000
        answers = []
        for i in range(len(ring_list)):
            c1 = ring_list[i].get_nm_location()
            c2 = self.get_nm_location()

            # Checks if the calculate distance is less than the current
            # smallest distance. If so, resets the answer list and adds
            # the newest ring.
            if get_distance(c1, c2) < distance:
                answers = []
                answers.append(ring_list[i])
                distance = get_distance(c1, c2)
            if get_distance(c1, c2) == distance:
                answers.append(ring_list[i])
            for ring in answers:
                self._rings.append(ring)
                # print(len(self._rings))
                ring.set_atom(self)
            self._d1 = distance

    def _findSecond(self, ring_list, x_max, y_max, edge_buffer):
        """ Finds the second closest ring center to the atom. If there
            are equidistant centers, puts all into self._rings. """
        if self.is_edge(x_max, y_max, edge_buffer):
            return
        distance = 100000000000000000000
        answers = []
        for i in range(len(ring_list)):
            c1 = ring_list[i].get_nm_location()
            c2 = self.get_nm_location()
            dist_2 = get_distance(c1, c2)
            if dist_2 < distance and dist_2 > self._d1:
                answers = []
                answers.append(ring_list[i])
                distance = dist_2
            if dist_2 == distance and dist_2 > self._d1:
                answers.append(ring_list[i])
            for ring in answers:
                self._rings.append(ring)
                ring.set_atom(self)
            self._d2 = distance

    def _findThird(self, ring_list, x_max, y_max, edge_buffer):
        """ Finds the second closest ring center to the atom. """
        if self.is_edge(x_max, y_max, edge_buffer):
            return
        distance = 100000000000000000000
        answers = []
        for i in range(len(ring_list)):
            c1 = ring_list[i].get_nm_location()
            c2 = self.get_nm_location()
            dist_2 = get_distance(c1, c2)
            if dist_2 < distance and dist_2 > self._d2:
                answers = []
                answers.append(ring_list[i])
                distance = dist_2
            if dist_2 == distance and dist_2 > self._d2:
                answers.append(ring_list[i])
            for ring in answers:
                self._rings.append(ring)
                ring.set_atom(self)
            self._d3 = distance


class ring_center:
    """ Contains the location of the ring center, and the type of ring
        (number of members). Objects do not automatically calculate their
        locations if you do not tell them to. NOTE: The main functionality is
        done in nanometers.  Pixel locations are held on to so they can be easy
        to grab, but, if you start calling complex methods with pixel
        dimensions, you're going to have a bad time. """

    def __init__(self, ring_type, x, y, z, unit):
        """ Constructor. """
        self._ring_type = ring_type
        if unit == "nm":
            self._nm_location = [x, y, z]
            self._pixel_location = [0, 0, 0]
        else:
            self._pixel_location = [x, y, z]
            self._nm_location = [0, 0, 0]
        self._atoms = []

    def get_nm_location(self):
        """ Returns the location in (x, y, z) form. Units are nm. """
        return self._nm_location

    def get_pix_location(self):
        """ Returns the location in (x, y, z) form. Units are Pixels"""
        return self._pixel_location

    def get_type(self):
        """returns type of ring"""
        return self._ring_type

    def set_atom(self, atom):
        """ Puts an atom into self._atoms. """
        self._atoms.append(atom)

    def get_atoms(self):
        """ Returns the atom list """
        return self._atoms

    def remove(self, index):
        """ Removes an atom from the atom list BY INDEX """
        del self._atoms[index]




class STM:
    """ A class to describe the STM image. Includes information like filename,
    Image Dimensions (pixels), sample dimensions (nm), scale, number of holes,
    and coordinates of those holes."""

    def __init__(self, filename, im_dim, sample_dim, num_holes):
        """ Constructor. """
        self._filename = filename
        self._im_dim = im_dim  # [image HEIGHT, image width] (pixels) flipped!
        self._sample_dim = sample_dim  # [sample width, sample height] (nm)
        self._scale = im_dim[0] / sample_dim[1]  # ratio pixels/nm
        self._num_holes = num_holes
        self._hole_coords = []
        self._hole_nm_coords = []
        self._hole_dists = [] # List of the distance of each center to nearest hole edge in nm
        self._rings = []
        self._Sis = []
        self._Os = []

    def get_filename(self):
        return self._filename

    def get_im_dim(self):
        return self._im_dim

    def get_sample_dim(self):
        return self._sample_dim

    def get_scale(self):
        return self._scale

    def get_num_holes(self):
        return self._num_holes

    def find_nm_location(self, object):
        """ Finds the coordinates of an object in nm when pixel coordinates are known."""
        for i in range(3):
            object._nm_location[i] = (1 / self._scale) * object._pixel_location[i]

    def find_pix_location(self, object):
        """ Finds the coordinates of an object in pixels when nm coordinates are known."""
        for i in range(3):
            object._pixel_location[i] = self._scale * object._nm_location[i]

    def get_hole_coords(self, greyscale):
        """ Gets coordinates of borders of holes from greyscale image """
        if self._num_holes > 0:
            #Threshold greyscale image to create a binary image
            im_thresh = filters.threshold_minimum(greyscale)
            binary = greyscale > im_thresh

            #Erode the binary image and subtract from original to get borders
            erosion = numpy.pad(morphology.binary_erosion(binary)[2:-2,2:-2],2,
                                'maximum')
            borders = binary ^ erosion
            borders = numpy.pad(borders[1:-1,1:-1],1,'edge')

            #Label the regions in the image
            label_image = measure.label(borders)
            regions = measure.regionprops(label_image)

            #Put all of the areas of regions in border image into list
            areas = [region.area for region in regions]

            #Get the coords of the largest num_holes number of border regions
            self._hole_coords = []
            for i in range(self._num_holes):
                max_ind = numpy.argmax(areas)
                coords = regions[max_ind].coords
                for coord in coords:
                    self._hole_coords.append([coord[1], coord[0]])

                del regions[max_ind]
                del areas[max_ind]
        else:
            self._hole_coords = []
        return self._hole_coords

    def get_hole_image(self):
        """ Takes the coordinates of the borders of the holes and fills them in
            to get a mask image of the holes """
        hole_image = numpy.zeros(self._im_dim)

        for coord in self._hole_coords:
            hole_image[coord[1],coord[0]] = 1

        return ndi.binary_fill_holes(morphology.binary_closing(hole_image))

    def plot_circles(self, image, coords, radius, color, reversed):
        """ Plots circles of a given radius and color on a given image at given
            coordinates """
        i, j = 1, 0
        if reversed:
            i, j = 0, 1
        for coord in coords:
            rr, cc = draw.circle(coord[i], coord[j], radius, shape=self._im_dim)
            image[rr, cc] = color

    def centers_to_objects(self, ring_size, center_list, unit):
        """Converts list of centers to center objects and puts in ring list"""
        for i in range(len(center_list)):
            center = ring_center(ring_size[i], center_list[i][0], center_list[i][1], 0, unit)
            if unit != "nm":
                self.find_nm_location(center)
            else:
                self.find_pix_location(center)
            self._rings.append(center)

    def Sis_to_objects(self, si_list, unit, x_max, y_max, edge_buffer):
        """Converts list of si coords to Si objects and puts in Sis list"""
        for loc in si_list:
            si = Si(loc[0], loc[1], loc[2], unit)
            if unit != "nm":
                self.find_nm_location(si)
            else:
                self.find_pix_location(si)
            si.find_rings(self._rings, x_max, y_max, edge_buffer)
            self._Sis.append(si)

    def getNumNeighbors(self, centers, thresh, average_closest, num_holes):
        """Edits distance to hole (nm), ring sizes, ring center coordinates, and  hole coordinates (nm)"""
        # Get distances and indices of 9 nearest neighbors to every center

        # STM function and call it as STM function
        def getNearestNeighbors(base_coords, search_coords, num_neighbors):
            nearest = NearestNeighbors(n_neighbors=num_neighbors, algorithm='ball_tree').fit(base_coords)
            dist, ind = nearest.kneighbors(search_coords)
            return dist, ind

        distances, indices = getNearestNeighbors(centers, centers, 10)

        # Gets the distances from every center to the nearest point on the edge of a hole
        if num_holes > 0:
            hole_distances, hole_inds = getNearestNeighbors(self._hole_coords, centers, 2)

        hole_dists = [] # List of the distance of each center to nearest hole edge in pixels
        ring_size = [] # List of size of each ring
        center_coords = [] # PUT RING CENTERS INTO -rings
        for k in range(len(distances)):
            n_dists = distances[k]

            # Averages the distances to closest 4 centers and multiplies by a
            # threshold to get the max distance for something to be a neighbor
            max_dist = numpy.mean(n_dists[1:5]) * thresh

            #Determines how many of the neighbors are within the max distance
            num_neighbors = 9
            for i in range(4,10):
                if n_dists[i] > max_dist:
                    num_neighbors = i - 1
                    break

            r_full, c_full = draw.circle(centers[k][1], centers[k][0], max_dist)
            r_bound, c_bound = draw.circle(centers[k][1], centers[k][0], max_dist, shape=self._im_dim)

            # Gets the perc of the ring neighbors that are visible in the window
            percent_visible = len(r_full) / len(r_bound)

            # Scales the number of neighbors based on what it should be if all the
            # ring neighbors were visible
            scaled_num_neighbors = int(num_neighbors * percent_visible)

            nearest_centers = []
            for i in range(1, num_neighbors+1):
                nearest_centers.append(centers[indices[k][i]][:])

            #Calculates the centroid of neighboring centers
            x = [p[0] for p in nearest_centers]
            y = [p[1] for p in nearest_centers]
            centroid = (sum(x) / len(nearest_centers), sum(y) / len(nearest_centers))

            exclude_thresh = 1.9

            if num_holes > 0:
                cur_hole_dist = hole_distances[k][1]
            else:
                cur_hole_dist = 2 * exclude_thresh * average_closest

            #Gets the coordinates of the circles around the centers
            if (4 <= scaled_num_neighbors <= 9 and percent_visible < 1.2 and
                cur_hole_dist > exclude_thresh * average_closest):
                hole_dists.append(cur_hole_dist)
                ring_size.append(scaled_num_neighbors)
                center_coords.append([(centers[k][0]+centroid[0])/2,(centers[k][1]+centroid[1])/2])

        self._hole_nm_coords = [] #converts hole coords to nm
        for coord in self._hole_coords:
            self._hole_nm_coords.append([coord[0] / self._scale, coord[1] / self._scale])

        self._hole_dists = [] #converts hole_dists to nm
        for dist in hole_dists:
            self._hole_dists.append(dist * self._scale)

        self.centers_to_objects(ring_size, center_coords, "pix")
