import pygame
import random

class Actor:
        '''Something occupying a space on the stage, it has an icon, position,
        delay, and can die(be removed from the stage
        '''
        def __init__(self, icon_file, stage, x, y, delay=5):
                self._icon=pygame.image.load(icon_file) # the image to display
                self.set_position(x, y) # self's location on the stage
                self._stage=stage # the stage that self is on
                self._delay=delay # the Actors 'speed' relative to other actors
                self._delay_count=0# used by delay to alter the actor's speed
                self._is_dead=False#Controls whether the actor is on the stage
        
        def set_position(self, x, y):
                (self._x, self._y) = (x, y)

        def get_position(self):
                return (self._x, self._y)

        def get_icon(self):
                return self._icon
        
        def infront_moveable(self, new_x, new_y, dx, dy):
                '''After asking the Actor at new_x and new_y (with respect to
                self) to move dx, dy, return whether the Actor infront moved
                and move accordingly
                '''
                infront = self._stage.get_actor(new_x, new_y)
                if infront != None:
                        if not infront.move(self, dx, dy):
                                return False
                return True

        def move(self, other, dx, dy):
                ''' other is telling us to move in direction (dx, dy), in this
                case, we just move. (dx,dy) is in {(1,1), (1,0), (1,-1), (0,1),
                (0,0), (0,-1), (-1,1), (-1,0), (-1,-1)} 
                '''
                self.set_position(self._x+dx, self._y+dy)
                return True

        def delay(self):
                ''' Used to change self's speed relative to other Actors. 
                Each time we get a chance to take a step, we delay. If our count
                wraps around to 0 then we actually do something. Otherwise, we
                simply return from the step method.
                '''
                self._delay_count=(self._delay_count+1)% self._delay
                return self._delay_count==0

        def step(self):
                ''' self takes a single step in the animation of the game.
                self can ask the stage to help as well as ask other Actors
                to help us get our job done. Also removes dead actors
                '''
                if self.is_dead():
                        self._stage.remove_actor(self)
                        
        def is_dead(self):
                return self._is_dead
        
        def kill(self):
                self._is_dead = True

        def evolve_into(self, class_object, icon_file, delay=5):
                ''' Replace self with an actor of a new class from class_object
                '''

                if not self._is_dead:
                        self.kill()
                        
                self._stage.add_actor(class_object(icon_file, self._stage,
                                                   self._x, self._y, delay))
                
                
class Player(Actor):
        ''' A Player is an Actor that can handle events. These typically come
        from the user, for example key presses etc. '''

        def __init__(self, icon_file, stage, x=0, y=0, player_number = 1):
                Actor.__init__(self, icon_file, stage, x, y, player_number)
                self._player_number = player_number
                #player_number needed to identify players in co-op mode
        
        def handle_event(self, event):
                ''' Used to register the occurrence of an event with self. '''
                pass
        
        def get_player_number(self):
                '''return the player number (to identify player objects)
                '''
                return self._player_number

class KeyboardPlayer(Player):
        ''' A KeyboardPlayer is a Player that can handle keypress events '''
        
        def __init__(self, icon_file, stage, x=0, y=0, player_number = 1):
                Player.__init__(self, icon_file, stage, x, y, player_number)
                self._last_event = None # we are only interested in the last event
        
        def handle_event(self, event):
                ''' Record the last event directed at this KeyboardPlayer, self
                ignores all previous events since self last took a step.
                '''
                self._last_event=event 
        
        def step(self):
                ''' Take a single step in the animation. 
                For example: if the user asked us to move right, then we do that. '''

                #players are removed differently from the stage
                if self.is_dead():
                        self._stage.remove_player(self)
                     
                if self._last_event is not None:

                        dx, dy= None, None

                        #for player1 controls
                        if self._player_number == 1:
                                if self._last_event==pygame.K_x:
                                        dx, dy=0,1
                                if self._last_event==pygame.K_s:
                                        dx, dy=-1,0   
                                if self._last_event==pygame.K_d:
                                        dx, dy =1,0      
                                if self._last_event==pygame.K_e:
                                        dx, dy =0,-1        
                                if self._last_event==pygame.K_w:
                                        dx, dy=-1,-1
                                if self._last_event==pygame.K_r:
                                        dx, dy=1,-1       
                                if self._last_event==pygame.K_z:
                                        dx, dy =-1,1        
                                if self._last_event==pygame.K_c:
                                        dx, dy =1,1
                        
                        #for player2 controls
                        if self._player_number == 2: 
                                if self._last_event==pygame.K_n:
                                        dx, dy=0,1
                                if self._last_event==pygame.K_h:
                                        dx, dy=-1,0
                                if self._last_event==pygame.K_j:
                                        dx, dy=1,0
                                if self._last_event==pygame.K_u:
                                        dx, dy=0,-1    
                                if self._last_event==pygame.K_y:
                                        dx, dy=-1,-1
                                if self._last_event==pygame.K_i:
                                        dx, dy=1,-1
                                if self._last_event==pygame.K_b:
                                        dx, dy =-1,1
                                if self._last_event==pygame.K_m:
                                        dx, dy =1,1
                                        
                        if (dx is not None) and (dy is not None):
                                self.move(self, dx, dy) # we are asking ourself to move

                        self._last_event=None 

        def move(self, other, dx, dy):
                ''' other is telling us to move in direction (dx, dy), move
                (when possible) and return whether moved in that direction. 
                '''
                #sets where this player plans to move
                new_x = self._x + dx
                new_y = self._y + dy
                
                if not self._stage.is_in_bounds(new_x, new_y):
                        return False
                
                if other != self: #no one pushes me around
                        return False

                if self.infront_moveable(new_x, new_y, dx, dy):
                        return Actor.move(self, other, dx, dy)
                
                return False
                               
class Box(Actor):
        '''An actor that can be moved around by Player and trap monsters (may
        have special abilities)
        '''
        
        def move(self, other, dx, dy):
                ''' other is telling us to move in direction (dx, dy), move
                (when possible) and return whether moved in that direction. 
                '''

                new_x = self._x + dx
                new_y = self._y + dy
                
                if not self._stage.is_in_bounds(new_x,new_y): 
                        return False
                        
                if self.infront_moveable(new_x, new_y, dx, dy):
                        return Actor.move(self, other, dx, dy)
                
                return False
        

class Ice_Box(Box):
        ''' A special kind of box that can freeze mosters when a introduced to
        them (also known as sticky box)
        '''
        def __init__(self, icon_file, stage, x=0, y=0, delay = 5):
                Box.__init__(self, icon_file, stage, x, y, delay)
                self._frozen_monsters = []
                #needed to store monster objects that are frozen
                #delay needed in order to have things evolve into it

        def add_to_frozen(self, monster):
                self._frozen_monsters.append(monster)

        def move(self, other, dx, dy):
                ''' other is telling us to move in direction (dx, dy), move
                (when possible) and return whether moved in that direction. 
                '''
                if Box.move(self, other, dx, dy):
                        #removes all the monsters that are stuck to the box and
                        #resets there frozen state
                        while self._frozen_monsters != []:
                                self._frozen_monsters.pop().set_frozen(False)
                        return True
                return False
        

class Wall(Box):
        '''A special kind of Actor that cannot be moved (Also known as Earth_Wall)
        '''
        def move(self, other, dx, dy):
                return False #Nothing can move a wall
        
class Fire_Wall(Wall):
        '''A special kind of Wall that replaces anything that tries to move it
        with itself
        '''     
        def move(self, other, dx, dy):
                if isinstance(other, Ice_Box): 
                        self.kill() #Ice_Boxes can 'put out' Fire_Walls
                        return True
                other.evolve_into(Fire_Wall, "icons/flames.jpg")
                     
class Monster(Actor):
        ''' A special type of actor that kills players and moves independently
        '''
        def __init__(self, icon_file, stage, x=0, y=0, delay=5):
                Actor.__init__(self, icon_file, stage, x, y, delay)
                self._dx=1
                self._dy=1
                self._is_frozen = False
                #indicates whether the monster is stuck to the box

        def set_frozen(self, frozen_bool):
                self._is_frozen = frozen_bool
                
        def is_dead(self):
                ''' Return whether self has died. That is, if self is surrounded
                on all sides, by either Boxes or other Monsters or the bounds of
                the stage.
                '''
                if not Actor.is_dead(self):
                        for x in range(-1,2): 
                                for y in range(-1,2):

                                        around = self._stage.get_actor(
                                                self._x+x, self._y+y)
                                        
                                        if(self._stage.is_in_bounds(self._x+x,
                                                                    self._y+y)
                                           
                                        and (around == None or isinstance(
                                                around, Player))):
                                                return False                                                                       
                self.kill()
                return True

        def step(self):
                ''' self takes a single step in the animation of the game.
                Also removes dead monsters or delays them accordingly
                '''
                Actor.step(self)
                if not self.delay():
                        return
                
                if not self._is_frozen: #do not move if frozen
                        self.move(self, self._dx, self._dy)
                        
                return True

        def move(self, other, dx, dy):
                ''' other asked self to move if possible, return whether I
                moved '''

                new_x = self._x + self._dx
                new_y = self._y + self._dy

                #if either coordinate is out of bounds, reflect the change
                #in that that coordinate
                bounce_off_edge=False
                
                if not self._stage.is_in_bounds_x(new_x): 
                        self._dx=-self._dx
                        bounce_off_edge=True
                        
                if not self._stage.is_in_bounds_y(new_y):
                        self._dy=-self._dy
                        bounce_off_edge=True


                #depending on what is asking to move, behave accordingly
                if isinstance(other, Player):
                        other.kill()
                        
                if isinstance(other, Ice_Box):
                        if not self._is_frozen:
                                other.add_to_frozen(self)
                                self._is_frozen = True
                                return False
                        
                if other != self: #no one pushes me around
                        return False


                #depending on what is infront of me, behave accordingly
                infront = self._stage.get_actor(new_x, new_y)
                if isinstance(infront, Ice_Box):
                        if not self._is_frozen:
                                infront.add_to_frozen(self)
                                self._is_frozen = True
                                return False

                #Fire_Walls can kill monsters or make them evolve where
                #applicable    
                if isinstance(infront, Fire_Wall):
                        self.kill() 
                        return False
                
                #Monsters bounce off of boxes or other monsters
                if isinstance(infront, Box) or isinstance(infront, Monster):
                        self._dx=-self._dx
                        self._dy=-self._dy
                        bounce_off_edge = True
                        
                if isinstance(infront, Player):
                        infront.kill()
                      
                if bounce_off_edge:
                        return False
                
                return  Actor.move(self, other, dx, dy)

class Shy_Monster(Monster):
         ''' A special kind of monster that looks like a box at some times and
         moves sparatically when the player is near
         '''
         def __init__(self, icon_file, disguise_file , stage, x=0, y=0, delay=5):
                 Monster.__init__(self, icon_file, stage, x, y, delay)
                 self._diguise = pygame.image.load(disguise_file)

         def surroundings(self, class_object):
                 '''Find the specfic object of class_object near self, if not present,
                 return the arbitrary coordinates (0,0) (which may be interpreted as
                 dx and dy, therefore making movement stop)
                 '''
                 for x in range(-1,2): 
                        for y in range(-1,2):
                                if self._stage.is_in_bounds(self._x+x,self._y+y):
                                        around = self._stage.get_actor(self._x+x,
                                                                       self._y+y)
                                        if isinstance(around, class_object):
                                                return (x,y)
                 return (0, 0)
                
         def run_away(self):
                 '''finds the direction of an empty location to move towards when the
                 player is near
                 '''
                 x, y = self.surroundings(Player)
                 if x != 0 and y != 0:
                         self._dx, self._dy = self.surroundings(type(None))

         def move(self, other, dx, dy):
                 ''' only move when the player is near, since the monster is
                 shy, it will not try to move into the player, but if the player
                 moves into the monster, it dies
                 '''
                 #while not moving, need to check for Ice_boxes
                 if isinstance(other, Ice_Box):
                        if not self._is_frozen:
                                other.add_to_frozen(self)
                                self._is_frozen = True
                                return False
                        
                 x, y = self.surroundings(Player)
                 if x == 0 and y == 0:
                         return False
                        
                 #while not moving, need to check for Players
                 if isinstance(other, Player):
                         other.kill()
                         return True
                        
                 if isinstance(self._stage.get_actor(self._x + self._dx,
                                            self._y + self._dy), Player):
                         return False
                 
                 else:
                         return Monster.move(self, other, dx, dy) 
                                                
         def step(self):
                 Monster.step(self)
                 self.run_away()
                                 
         def is_dead(self):
                ''' Return whether self has died and evolve accordingly  '''

                if Monster.is_dead(self):
                        for x in range(-1,2): 
                                for y in range(-1,2):
                                        around = self._stage.get_actor(
                                                self._x+x, self._y+y)
                                        
                                        if isinstance(around, Box):
                                                around.kill()
                                                
                        self.evolve_into(Stalker_Monster,
                                         'icons/Monsters/purple_monster.png')
                        return True
                
                return False
                                                                              
                

         def get_icon(self):
                '''randomly change the monsters icon to its true self or its
                disguise
                '''
                if random.randrange(0,10) == 7:
                        return self._icon
                else:
                        return self._diguise


class Stalker_Monster(Monster):
        '''A special kind of monster that follows the player around on screen
        '''
        
        def stalk(self):
                player1, player2 = self._stage.get_players()

                if player1 == None and player2 == None:
                        self._dx, self._dy = 0,0
                else:
                        if player1 != None and player2 != None:
                                player_x, player_y = player1.get_position()

                        if player1 == None:
                                player_x, player_y = player2.get_position()

                        if player2 == None:
                                player_x, player_y = player1.get_position()
                        
                        if player_x == self._x:
                                self._dx = 0
                                
                        elif player_x < self._x:
                                self._dx = -1
                        
                        else:
                                self._dx = 1
                        
                        if player_y == self._y:
                                self._dy = 0
                        
                        elif player_y < self._y:
                                self._dy = -1
                        
                        else:
                                self._dy = 1
        
        def step(self):
                 Monster.step(self)
                 self.stalk()

class Fire_Monster(Monster):
         ''' A special kind of monster that turns into a Fire_Wall when dead
         '''
 
         def is_dead(self):
                ''' Return whether self has died and evolve accordingly  '''

                if Monster.is_dead(self):
                        self.evolve_into(Fire_Wall, 'icons/Boxes/flame_box.png')
                        return True
                return False
        
class Earth_Monster(Monster):
         ''' A special kind of monster that turns into an Earth_Wall (aka Wall)
         when dead
         '''

         def is_dead(self):
                ''' Return whether self has died and evolve accordingly  '''

                if Monster.is_dead(self):
                        self.evolve_into(Wall, 'icons/Boxes/earth_box.png')
                        return True
                return False
        
class Ice_Monster(Monster):
         ''' A special kind of monster that turns into an Ice_Box aka Sticky Box
         when dead
         '''
        
         def is_dead(self):
                ''' Return whether self has died and evolve accordingly  '''

                if Monster.is_dead(self):
                        self.evolve_into(Ice_Box, 'icons/Boxes/ice_box.png')
                        return True
                return False

class Stage:
        
        def __init__(self, width, height, icon_dimension, pic, colour = 0,
                     colour_change = 5):

                # all actors on this stage (monsters, player, boxes, ...)
                self._actors=[] 

                #special actors, the players
                self._player1 = None 
                self._player2 = None 
                
                # the logical width and height of the stage
                self._width, self._height = width, height
                
                # the pixel dimension of all actors
                self._icon_dimension=icon_dimension
                
                # the pixel dimensions of the whole stage
                self._pixel_width = self._icon_dimension * self._width
                self._pixel_height = self._icon_dimension * self._height
                self._pixel_size = self._pixel_width, self._pixel_height

                # get a screen of the appropriate dimension to draw on
                self._screen = pygame.display.set_mode(self._pixel_size)
                self._stage_pic = pic #background of the stage
                self._colour = colour #starting colour number 
                self._colour_change = colour_change
                #the factor that the stage colour changes by

                self._is_winner = False

        def is_in_bounds(self, x,y):
                return self.is_in_bounds_x(x) and self.is_in_bounds_y(y)

        def is_in_bounds_x(self, x):
                return 0<=x and x<self._width

        def is_in_bounds_y(self, y):
                return 0<=y and y<self._height

        def get_width(self): 
                return self._width

        def get_height(self): 
                return self._height
        
        def is_winner(self):
                return self._is_winner

        def set_player(self, player1, player2 = None):
                ''' A Player is a special actor, self may need to contact them
                directly
                '''

                self._player1 = player1
                self.add_actor(self._player1)
                
                self._player2 = player2
                
                if player2 != None:#in single player mode, player2 doesn't exist
                        self.add_actor(self._player2)
                                        
        def get_players(self):
                return (self._player1, self._player1) 

        def remove_player(self, other):

                #The identity of the player is necessary to remove the correct
                #actor, so player_number is a must
                if other.get_player_number() == 1:
                        self.remove_actor(self._player1)
                        self._player1=None
                        
                elif other.get_player_number() == 2:
                        self.remove_actor(self._player2)
                        self._player2=None
                        
                

        def player_event(self, event):
                ''' Send a user event to the player (this is a special Actor).
                '''
                movement_p1 = [pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_c,
                               pygame.K_s, pygame.K_d, pygame.K_z, pygame.K_x]
                
                movement_p2 = [pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_h,
                               pygame.K_j, pygame.K_b, pygame.K_n, pygame.K_m]

                #because one player can die while the other lives, None must
                #be checked for both players
                if (self._player1 != None) and (event in movement_p1):
                    self._player1.handle_event(event)

                elif (self._player2 != None) and  (event in movement_p2):
                    self._player2.handle_event(event)

        def add_actor(self, actor):
                self._actors.append(actor)

        def remove_actor(self, actor):
                self._actors.remove(actor)        

        def step(self):
                ''' Take one step in the animation of the game. 
                Do this by asking each of the actors to take a single step. '''

                for a in self._actors:
                        a.step()

        def get_actors(self):
                return self._actors

        def get_actor(self, x, y):
                ''' return the first actor at coordinates (x,y) 
                return None if there is no such actor
                '''
                for a in self._actors:
                        if a.get_position()==(x,y):
                                return a
                return None
        
        def game_over(self):
                
                if self._player1 != None or self._player2 != None:

                        for a in self._actors:
                                if isinstance(a, Monster):
                                        return False
                                
                        self._is_winner = True
                        return True
                
                return True
                
        def draw(self):
                ''' draw all Actors on self to the screen '''
                #colour the stage with the appropriate configuration (r,g,b),
                #(holding g and b at the same colour gives a shade of turquoise)
                self._screen.fill((0, self._colour, self._colour))
                self._screen.blit(self._stage_pic, (0,0))

                #self._colour must be oscillate between 0 and 75
                if self._colour == 75:
                        self._colour_change = -5
                elif self._colour == 0:
                        self._colour_change = 5
                        
                #The colour changes by 5 each draw execution
                self._colour += self._colour_change
                
                
                for a in self._actors:
                        icon=a.get_icon()
                        (x,y)=a.get_position()
                        d=self._icon_dimension
                        rect=pygame.Rect(x*d, y*d, d, d)
                        self._screen.blit(icon, rect)
                pygame.display.flip()


