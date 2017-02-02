import sys, pygame, random
from ww import *
pygame.init()

#Start Screen
screen = pygame.display.set_mode((442,700))
start_screen = pygame.image.load("icons/Screens/start_screen.png")
player_option = 0
colour=0 #starting colour of stage

while player_option == 0:
        for event in pygame.event.get():
                # based on the event type quit or load stage with 1 or 2 players
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            player_option = 1
                        if event.key == pygame.K_2:
                            player_option = 2

        #colour must be oscillate between 0 and 175                    
        if colour == 175:
                colour_change = -5
        elif colour== 0:
                colour_change = 5
        colour += colour_change

        screen.fill((0, colour, colour))
        screen.blit(start_screen, (0,0))
        pygame.display.flip()                    


ww=Stage(20, 20, 24, pygame.image.load("icons/Screens/stage.png"))

if player_option == 1:
        ww.set_player(KeyboardPlayer("icons/Players/player1.png", ww, 0, 0))
        
elif player_option == 2:
        ww.set_player(KeyboardPlayer("icons/Players/player1.png", ww, 0, 0, 1),
                       KeyboardPlayer("icons/Players/player2.png", ww, 0, 1, 2))

#Generate a safe spawn zone (diagonal with player 1 to exit)      
ww.add_actor(Wall("icons/Boxes/immovable_box.png", ww, 2, 0))
ww.add_actor(Wall("icons/Boxes/immovable_box.png", ww, 2, 1))
ww.add_actor(Wall("icons/Boxes/immovable_box.png", ww, 1, 2))
ww.add_actor(Wall("icons/Boxes/immovable_box.png", ww, 0, 2))


ww.add_actor(Monster("icons/Monsters/white_monster.png", ww, 1, 19, 1))

ww.add_actor(Shy_Monster("icons/Monsters/purple_monster.png",
                               "icons/Boxes/monster_disguise.png", ww, 18, 1))

ww.add_actor(Fire_Monster("icons/Monsters/red_monster.png", ww, 4, 16, 4))
ww.add_actor(Earth_Monster("icons/Monsters/green_monster.png", ww, 10, 17, 3))
ww.add_actor(Ice_Monster("icons/Monsters/dark_blue_monster.png", ww, 17, 18, 6))



#plot 100 boxes in places where there are not actors already
num_boxes=0
while num_boxes<100:
        x=random.randrange(ww.get_width())
        y=random.randrange(ww.get_height())
        if ww.get_actor(x,y) is None:
                ww.add_actor(Box("icons/Boxes/black_box.png", ww, x, y))
                num_boxes+=1


# while the game is not over, quit or pass an event to the player, then
# allow all actors to take a step and re-draw the stage
while not ww.game_over():
        pygame.time.wait(100)
        for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.KEYDOWN:
                        ww.player_event(event.key)                    
        ww.step()
        ww.draw()

#When the game is over display the game over screen
screen = pygame.display.set_mode((480,700))

if ww.is_winner():
        end_screen = pygame.image.load("icons/Screens/Winner.png")
        
if not ww.is_winner():
        end_screen = pygame.image.load("icons/Screens/Game_Over.png")
        
screen.blit(end_screen, (0,0))
pygame.display.flip()
sys.exit()


