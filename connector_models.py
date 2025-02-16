import cadquery as cq
import math

class ConnectorGenerator:
    def __init__(self, board_width, board_thickness, board_depth, 
                 wall_thickness=3, tolerance=0.2, add_taper=False,
                 add_ribs=False, add_screw_holes=False):
        self.board_width = board_width
        self.board_thickness = board_thickness
        self.board_depth = board_depth
        self.wall_thickness = wall_thickness
        self.tolerance = tolerance
        self.add_taper = add_taper
        self.add_ribs = add_ribs
        self.add_screw_holes = add_screw_holes

    def _create_basic_slot(self, length, with_taper=True):
        """Creates a slot for the board with optional taper"""
        slot_width = self.board_width + self.tolerance
        slot_height = self.board_thickness + self.tolerance
        slot = cq.Workplane("XY").box(length, slot_width, slot_height)

        if self.add_taper and with_taper:
            # Add a 45-degree taper at the entrance
            taper_depth = min(2, length/4)  # Limit taper depth
            taper = (cq.Workplane("XY")
                    .wedge(taper_depth, 
                          slot_width,    # ymin: width at base
                          slot_width + 2,  # ymax: width at tip
                          0,              # zmin: always 0
                          slot_height))   # zmax: height
            slot = slot.union(taper.translate((-length/2 - taper_depth/2, 0, -slot_height/2)))

        return slot

    def _add_screw_holes(self, workplane, depth):
        """Adds 5mm screw holes to the connector"""
        if not self.add_screw_holes:
            return workplane

        hole_diameter = 5
        hole_positions = []
        
        # Add holes based on connector depth
        if depth > 20:  # Only add holes if there's enough space
            hole_positions.append((depth/4, 0, 0))
            if depth > 40:  # Add second set of holes for longer connectors
                hole_positions.append((-depth/4, 0, 0))

        # Create holes
        for pos in hole_positions:
            workplane = (workplane
                        .faces(">Z")  # Select top face
                        .workplane()
                        .transformed(offset=pos)
                        .hole(hole_diameter))

        return workplane

    def _add_reinforcement_ribs(self, workplane, length, width, height):
        """Adds reinforcement ribs to the connector"""
        if not self.add_ribs:
            return workplane

        rib_thickness = min(2, self.wall_thickness - 0.5)
        rib_spacing = 20  # Space between ribs
        num_ribs = max(1, int(length / rib_spacing) - 1)

        for i in range(num_ribs):
            pos = length * (i + 1)/(num_ribs + 1) - length/2
            rib = (cq.Workplane("XY")
                  .box(rib_thickness, width, height))
            workplane = workplane.union(rib.translate((pos, 0, 0)))

        return workplane

    def create_end_to_end_connector(self):
        """Creates an end-to-end connector with slots for boards"""
        # Calculate dimensions
        connector_length = (self.board_depth * 2) + (self.wall_thickness * 2)  # Length for two full boards plus walls
        connector_width = self.board_width + (self.wall_thickness * 2)  # Add walls on sides
        connector_height = self.board_thickness + (self.wall_thickness * 2)  # Add walls top/bottom
        
        # Create outer shell
        result = (cq.Workplane("XY")
                 .box(connector_length, connector_width, connector_height))
        
        # Create slot (slightly larger than board for tolerance)
        slot = (cq.Workplane("XY")
               .box(connector_length + self.tolerance,
                   self.board_width + self.tolerance,
                   self.board_thickness + self.tolerance))
        
        # Cut slot
        result = result.cut(slot)
        
        if self.add_taper:
            # Create tapered entries
            taper_depth = min(2, self.wall_thickness)
            
            # Create taper for both ends
            taper = (cq.Workplane("XY")
                    .wedge(taper_depth,  # xlen (depth)
                          self.board_width + self.tolerance,    # ymin: width at base
                          self.board_width + self.tolerance + 1,  # ymax: width at tip
                          0,              # zmin: always 0
                          self.board_thickness + self.tolerance))   # zmax: height
            # Add tapers at both ends
            result = (result
                     .cut(taper.translate((-connector_length/2 - taper_depth/2, 0, -connector_height/2)))  # Left taper
                     .cut(taper.rotate((0,0,0), (0,0,1), 180)
                          .translate((connector_length/2 + taper_depth/2, 0, -connector_height/2))))  # Right taper
        
        if self.add_ribs:
            # Add reinforcement ribs
            rib_thickness = min(1.5, self.wall_thickness/2)  # Thinner ribs
            rib = (cq.Workplane("XY")
                  .box(rib_thickness, connector_width, connector_height))
            
            # Add three ribs for better support
            result = (result
                     .union(rib)  # Center rib
                     .union(rib.translate((-connector_length/4, 0, 0)))  # Left quarter
                     .union(rib.translate((connector_length/4, 0, 0))))  # Right quarter
        
        if self.add_screw_holes:
            # Add screw holes
            hole_diameter = 5
            hole_distance_from_end = self.board_depth/2  # Half of board depth
            
            # Two holes on top, half board depth from each end
            result = (result
                     .faces(">Z")  # Top face
                     .workplane()
                     .pushPoints([(-connector_length/2 + hole_distance_from_end, 0),
                                (connector_length/2 - hole_distance_from_end, 0)])
                     .hole(hole_diameter))
            
            # Two holes on bottom, half board depth from each end
            result = (result
                     .faces("<Z")  # Bottom face
                     .workplane()
                     .pushPoints([(-connector_length/2 + hole_distance_from_end, 0),
                                (connector_length/2 - hole_distance_from_end, 0)])
                     .hole(hole_diameter))
        
        return result

    def create_angle_connector(self, angle=90):
        """Creates an L-shaped connector with a solid corner and channels that stop at meeting point"""
        # Calculate dimensions
        board_length = self.board_depth  # Length of each board section
        board_width = self.board_width + (self.wall_thickness * 2)  # Add walls on sides
        board_height = self.board_thickness + (self.wall_thickness * 2)  # Add walls top/bottom
        corner_size = board_height  # Size of the solid corner
        
        # Create base of L shape with extended arms to accommodate the solid corner
        result = (cq.Workplane("XY")
                 # Create horizontal section (extended by corner_size)
                 .box(board_length + corner_size, board_height, board_width)
                 .translate(((board_length + corner_size)/2, board_height/2, board_width/2))
                 # Create vertical section (extended by corner_size)
                 .union(cq.Workplane("XY")
                       .box(board_height, board_length + corner_size, board_width)
                       .translate((board_height/2, (board_length + corner_size)/2, board_width/2))))
        
        # Create horizontal channel (stops at corner)
        h_channel = (cq.Workplane("XY")
                    .box(board_length,  # Original length
                        self.board_thickness,  # Board thickness
                        self.board_width)  # Board width
                    .translate((board_length/2 + corner_size,  # Shifted right by corner_size
                              board_height/2,  # Position at bottom of connector
                              board_width/2)))  # Center in Z
        
        # Cut horizontal channel
        result = result.cut(h_channel)
        
        # Create vertical channel (stops at corner)
        v_channel = (cq.Workplane("XY")
                    .box(self.board_thickness,  # Board thickness
                        board_length,  # Original length
                        self.board_width)  # Board width
                    .translate((board_height/2,  # Position at inner edge
                              board_length/2 + corner_size,  # Shifted up by corner_size
                              board_width/2)))  # Center in Z
        
        # Cut vertical channel
        result = result.cut(v_channel)
        
        if self.add_taper:
            # Create tapered entries
            taper_depth = min(2, self.wall_thickness)
            
            # Create horizontal taper
            h_taper = (cq.Workplane("XY")
                      .box(taper_depth, self.board_thickness + 2, board_width)
                      .faces(">X")
                      .workplane()
                      .transformed(offset=cq.Vector(0, 0, -board_width/4))
                      .rect(self.board_thickness + 2, board_width/2)
                      .loft()
                      .translate((board_length + corner_size, board_height/2, board_width/2)))
            
            # Add taper at the end of horizontal section
            result = result.cut(h_taper)
            
            # Create vertical taper
            v_taper = (cq.Workplane("XY")
                      .box(self.board_thickness + 2, taper_depth, board_width)
                      .faces(">Y")
                      .workplane()
                      .transformed(offset=cq.Vector(0, 0, -board_width/4))
                      .rect(self.board_thickness + 2, board_width/2)
                      .loft()
                      .translate((board_height/2, board_length + corner_size, board_width/2)))
            
            # Add taper at the end of vertical section
            result = result.cut(v_taper)
        
        if self.add_ribs:
            # Add reinforcement ribs
            rib_thickness = min(1.5, self.wall_thickness/2)
            
            # Create horizontal rib
            h_rib = (cq.Workplane("XY")
                    .box(rib_thickness, board_height, board_width)
                    .translate(((board_length + corner_size) * 0.75, board_height/2, board_width/2)))
            
            # Add rib to horizontal section
            result = result.union(h_rib)
            
            # Create vertical rib
            v_rib = (cq.Workplane("XY")
                    .box(board_height, rib_thickness, board_width)
                    .translate((board_height/2, (board_length + corner_size) * 0.75, board_width/2)))
            
            # Add rib to vertical section
            result = result.union(v_rib)
        
        if self.add_screw_holes:
            # Add screw holes
            hole_diameter = 5
            
            # Add hole to horizontal section
            result = (result
                     .faces(">Z")
                     .workplane()
                     .center((board_length + corner_size) * 0.75, board_height/2)
                     .hole(hole_diameter))
            
            # Add hole to vertical section
            result = (result
                     .faces(">Z")
                     .workplane()
                     .center(board_height/2, (board_length + corner_size) * 0.75)
                     .hole(hole_diameter))
        
        return result

    def create_t_connector(self):
        """Creates a T-shaped connector with proper slots for boards"""
        # Calculate dimensions for main body
        horizontal_length = (self.board_depth * 2) + (self.wall_thickness * 2)  # Length for two full boards plus walls
        vertical_length = self.board_depth + (self.wall_thickness * 2)    # Vertical section
        
        # Add walls around the board dimensions
        body_width = self.board_width + (self.wall_thickness * 2)
        body_height = self.board_thickness + (self.wall_thickness * 2)
        
        # Create main horizontal body
        result = (cq.Workplane("XY")
                 .box(horizontal_length, body_width, body_height))
        
        # Create vertical extension
        vertical_body = (cq.Workplane("XY")
                       .box(body_width, vertical_length, body_height)
                       .translate((0, body_width/2 + vertical_length/2, 0)))  # Position after horizontal body
        
        # Combine bodies
        result = result.union(vertical_body)
        
        # Create slots with tolerance
        slot_width = self.board_width + self.tolerance
        slot_height = self.board_thickness + self.tolerance
        
        # Horizontal slot through entire length
        h_slot = (cq.Workplane("XY")
                 .box(horizontal_length + self.tolerance,
                     slot_width,
                     slot_height))
        
        # Vertical slot - only in vertical section
        v_slot = (cq.Workplane("XY")
                 .box(slot_width,
                     vertical_length + self.tolerance,
                     slot_height)
                 .translate((0, body_width/2 + vertical_length/2, 0)))  # Match vertical body position
        
        # Cut slots from body
        result = result.cut(h_slot).cut(v_slot)
        
        if self.add_taper:
            # Create tapered entries
            taper_depth = min(2, self.wall_thickness)
            
            # Horizontal tapers
            h_taper = (cq.Workplane("XY")
                      .wedge(taper_depth,  # xlen (depth)
                            slot_width,    # ymin (base width)
                            slot_width + 1,  # ymax (tip width)
                            0,              # zmin (always 0)
                            slot_height))   # zmax (height)
            
            # Add horizontal tapers at both ends
            result = (result
                     .cut(h_taper.translate((-horizontal_length/2 - taper_depth/2, 0, -body_height/2)))
                     .cut(h_taper.rotate((0,0,0), (0,0,1), 180)
                          .translate((horizontal_length/2 + taper_depth/2, 0, -body_height/2))))
            
            # Vertical taper at top
            v_taper = h_taper.rotate((0,0,0), (0,0,1), 90)
            result = result.cut(v_taper.translate((0, body_width/2 + vertical_length, -body_height/2)))
        
        if self.add_ribs:
            # Add reinforcement ribs
            rib_thickness = min(1.5, self.wall_thickness/2)  # Thinner ribs
            
            # Horizontal ribs
            h_rib = (cq.Workplane("XY")
                    .box(rib_thickness, body_width, body_height))
            
            # Add three ribs for better support
            result = (result
                     .union(h_rib)  # Center rib
                     .union(h_rib.translate((-horizontal_length/4, 0, 0)))  # Left quarter
                     .union(h_rib.translate((horizontal_length/4, 0, 0))))  # Right quarter
            
            # Vertical rib
            v_rib = (cq.Workplane("XY")
                    .box(body_width, rib_thickness, body_height)
                    .translate((0, body_width/2 + vertical_length/4, 0)))
            result = result.union(v_rib)
        
        if self.add_screw_holes:
            # Add screw holes
            hole_diameter = 5
            hole_distance_from_end = self.board_depth/2  # Half of board depth
            
            # One hole on top for horizontal section
            result = (result
                     .faces(">Z")  # Top face
                     .workplane()
                     .center(0, 0)  # Center of horizontal section
                     .hole(hole_diameter))
            
            # One hole on bottom for horizontal section
            result = (result
                     .faces("<Z")  # Bottom face
                     .workplane()
                     .center(0, 0)  # Center of horizontal section
                     .hole(hole_diameter))
            
            # One hole for vertical section, half board depth from the end
            result = (result
                     .faces(">Z")  # Top face
                     .workplane()
                     .center(0, body_width/2 + vertical_length - hole_distance_from_end)  # Half board depth from end
                     .hole(hole_diameter))
        
        return result

    def create_cross_connector(self):
        """Creates a cross-shaped connector for joining boards"""
        # Calculate dimensions
        base_size = max(self.board_width, self.board_depth) * 2
        base_height = self.board_thickness + (self.wall_thickness * 2)
        
        # Create base piece
        result = (cq.Workplane("XY")
                 .box(base_size, base_size, base_height))
        
        # Create slot
        slot = self._create_basic_slot(self.board_depth/2)
        
        # Add slots in cross pattern
        result = (result
                 .cut(slot)
                 .cut(slot.rotate((0, 0, 0), (0, 0, 1), 90)))

        # Add reinforcement ribs
        if self.add_ribs:
            for angle in [0, 45, 90, 135]:
                rib = (cq.Workplane("XY")
                      .box(2, base_size, base_height)
                      .rotate((0, 0, 0), (0, 0, 1), angle))
                result = result.union(rib)

        # Add screw holes
        result = self._add_screw_holes(result, base_size)

        return result
