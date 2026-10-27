#a note: EVERYTHING IN HERE IS FREE TO USE FOR ANY PURPOSE EXCEPT:
    #starShieldFont

#importing necessary modules and intitiating stuff
import pygame
import time
import random

pygame.init()
pygame.font.init() 

#defining window stuff here
displayWidth = 1200
displayHeight = 800
gameName = "A Bit Spacey"
gameDisplay = pygame.display.set_mode((displayWidth,displayHeight))
pygame.display.set_caption(gameName)

black = (0,0,0)
white = (255,255,255)
red = (200,0,0)
green = (0,200,0)
blue = (0,0,200)

redder = (255,0,0)
greener = (0,255,0)
bluer = (0,0,255)

#font for the whole game
gameFont = "starShieldFont.ttf"

#clock def
clock = pygame.time.Clock()

#defining some sprite stuff
playerWidth = 120
playerHeight = 160 #unused

enemy1Width = 160
enemy1Height = 80

enemy2Width = 100
enemy2Height = 160 #unused

bossWidth = 610
bossHeight = 300

laserWidth = 90
laserHeight = 600

powerupWidth = 90
powerupHeight = 110

#other variables
gameMode = ""
secretMode = False

pause = False

enemy1Speed = 3
enemy1SpawnCount = 3

enemy2Speed = 2
enemy2SpawnCount = 2
eBulletStart = (0,0)

bossHealth = 100

playerCanShoot = 7
playerShootCooldown = 7
enemyShoot = False

bulletHitSpot = (0,0)

powerupType = str()
powerupDisplayType = str()
powerupColor = redder

powerupCanDisplay = False

score = 0

bossStage = False

playerBulletSpeed = 15
enemyBulletSpeed = 6
playerSpeed = 10
bossSpeed = 2
laserSpeed = 25

gameReset = False
gameOver = True
gameWin = True

#a bunch of sounds + getting music ready
playerCrashSound = pygame.mixer.Sound('playerCrash.mp3')
enemyCrashSound = pygame.mixer.Sound('enemyCrash.mp3')
gameOverSound = pygame.mixer.Sound('gameOver.mp3')
playerShootSound = pygame.mixer.Sound('playerShoot.mp3')
enemyShootSound = pygame.mixer.Sound('enemyShoot.mp3')
laserChargeSound = pygame.mixer.Sound('laserCharge.mp3')
laserFireSound = pygame.mixer.Sound('laserFire.mp3')
powerupSound = pygame.mixer.Sound('powerupGrab.mp3')
winGameSound = pygame.mixer.Sound('gameWin.mp3')
secretSound = pygame.mixer.Sound('secretClick.mp3')

#creating events
scoreIncrease = pygame.USEREVENT + 1
bossShoot = pygame.USEREVENT + 2
hIKill = pygame.USEREVENT + 3
powerupTextEnd = pygame.USEREVENT + 4

#sprite definitions
    #there are a bunch of "if secret mode...else" things, that changes visuals only if secret mode is enabled
class player(pygame.sprite.Sprite):
    #initalization
    def __init__(self):
        global secretMode

        super().__init__()
        
        if secretMode == False:
            self.image = pygame.image.load('playerShip.png')
        else:
            self.image = pygame.image.load('altSkins/playerShipAlt.png')
        
        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth * 0.5),(displayHeight * 0.5))
    
    #updating
    def update(self):
        global playerSpeed

        pressedKeys = pygame.key.get_pressed()

        #movement keys w/ BG parallax (magic numbers for parallax because speed up could break it otherwise)
        if (pressedKeys[pygame.K_UP]) and (p1.rect.top > 0):
            self.rect.move_ip(0,(-playerSpeed/2))
            bG1.rect.move_ip(0,1)
        if (pressedKeys[pygame.K_DOWN]) and (p1.rect.bottom < displayHeight):
            self.rect.move_ip(0,(playerSpeed/2))
            bG1.rect.move_ip(0,-1)
        if (pressedKeys[pygame.K_LEFT]) and (p1.rect.left > 0):
            self.rect.move_ip((-playerSpeed),0)
            bG1.rect.move_ip(2,0)
        if (pressedKeys[pygame.K_RIGHT]) and (p1.rect.right < displayWidth):
            self.rect.move_ip(playerSpeed,0)
            bG1.rect.move_ip(-2,0)

    #drawing
    def draw(self,surface):
        surface.blit(self.image,self.rect)

class playerBullet(pygame.sprite.Sprite):
    #grabbing globals
    global playerBulletSpeed

    #making pBulletPierce here so it can be different between instances
    pBulletPierce = 0

    #initialization
    def __init__(self):
        super().__init__()

        if secretMode == False:
            self.image = pygame.image.load('playerBullet.png')
        else:
            self.image = pygame.image.load('altSkins/bulletAlt.png')

        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth * 0.5),(displayHeight * -0.2))

    #does this when player shoots (see player update)
    def shoot(self):
        global activePlayerBullet

        activePlayerBullet = playerBullet()
        playerProjectiles.add(activePlayerBullet)
        allSprites.add(activePlayerBullet)
        activePlayerBullet.rect.center = ((p1.rect.left + (playerWidth/2)),(p1.rect.top))

    #updating
    def update(self):
        global bulletHitSpot
        global bossStage
        
        if (self in playerProjectiles):
            #movement
            self.rect.move_ip(0,-playerBulletSpeed)
        
            #killing once going to top of screen (collision detected in THELOOP)
            if (self.rect.bottom < 0):
                self.kill()
            
            #collision for normal enemies is put here so that bullet pierce going down works
            #deactivates at boss tho so the boss doesn't instantly die
            if (pygame.sprite.spritecollide(self,enemies,0)) and (bossStage == False):
                #checks mask collision specifically
                if pygame.sprite.spritecollide(self,enemies,1,pygame.sprite.collide_mask):
                    #indicator
                    bulletHitSpot = self.rect.midtop
                    hI.showHit()

                    #bullet kill OR reduce pierce if applicable
                    if self.pBulletPierce == 0:
                        self.kill()
                    else:
                        self.pBulletPierce -= 1
                    
                    #kill enemy noise
                    pygame.mixer.Sound.play(enemyCrashSound)

    #drawing
    def draw(self,surface):
        surface.blit(self.image,self.rect)

class enemyBullet(pygame.sprite.Sprite):
    #initializing source sprite
    def __init__(self):
        super().__init__()

        if secretMode == False:
            self.image = pygame.image.load('enemyBullet.png')
        else:
            self.image = pygame.image.load('altSkins/bulletAlt.png')

        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth * 0.5),(displayHeight * -0.2))
    
    def shoot(self):
        global activeEnemyBullet

        activeEnemyBullet = enemyBullet()
        enemyProjectiles.add(activeEnemyBullet)
        allSprites.add(activeEnemyBullet)
        activeEnemyBullet.rect.center = (eBulletStart)

    def update(self):
        global enemyBulletSpeed
        global score

        #moves downward if active
        if self in enemyProjectiles:
            self.rect.move_ip(0,enemyBulletSpeed)
        
        #kill once past bottom of screen
        if (self.rect.top > displayHeight):
                self.kill()
    
    def draw(self,surface):
        surface.blit(self.image,self.rect)

class bossLaser(pygame.sprite.Sprite):
    #initialization
    def __init__(self):
        super().__init__()

        if secretMode == False:
            self.image = pygame.image.load('bossLaser.png')
        else:
            self.image = pygame.image.load('altSkins/bossLaserAlt.png')

        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth * 0.5),(-laserHeight))
    
    def update(self):
        global laserSpeed

        #goes down until offscreen, then dies (also stays at boss horizontal center)
        if (self in enemyProjectiles):
            #plays sound at right point
            if (activeBoss.rect.bottom > self.rect.bottom > (activeBoss.rect.bottom - 35)):
                pygame.mixer.Sound.play(laserFireSound)
            if (self.rect.top < displayHeight):
                self.rect.move_ip(0,laserSpeed)
                self.rect.left = (activeBoss.rect.center[0] - laserWidth * 0.5)
            else:
                self.kill()
    
    def shoot(self):
        global activeEnemyBullet

        #creates active version then sends it to eBulletStart, which is set in BOSSLOOP()
        activeLaser = bossLaser()
        enemyProjectiles.add(activeLaser)
        allSprites.add(activeLaser)
        activeLaser.rect.center = (eBulletStart)

    def draw(self,surface):
        surface.blit(self.image,self.rect)

class enemy1(pygame.sprite.Sprite):
    driftDirection = int()
    e1CanDrift = 0
    
    #initialization
    def __init__(self):
        super().__init__()

        if secretMode == False:
            self.image = pygame.image.load('enemyShip1.png')
        else:
            self.image = pygame.image.load('altSkins/enemyShip1Alt.png')

        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth * 0.5),(displayHeight * -0.2))

    #updating
    def update(self):
        global enemy1Speed
        global score

        enemy1().driftDirection

        if self in enemies:
            self.rect.move_ip(0,enemy1Speed)
            if (self.rect.top > displayHeight):
                GAMEOVERLOOP()
            
            self.drift()
            #moves horizontally based on driftDirection, with safeguard from going
            #offscreen. this is meant to be the passive movement
            if (self.rect.left > 0) and (self.rect.right < displayWidth):
                self.rect.move_ip((enemy1Speed * self.driftDirection),0)
            elif (self.rect.left > 0):
                self.rect.move_ip(-enemy1Speed,0)
            else:
                self.rect.move_ip(enemy1Speed,0)
    
    def drift(self):
        #this is a cooldown toggle, basically


        #chooses a random direction every 45 frames, then sets direction to pos or neg
        if (self in enemies) and (enemy1.e1CanDrift == 45):
            self.driftDirection = random.choice([-1,0,1])
            enemy1.e1CanDrift = 0
        else:
            enemy1.e1CanDrift += 1

    #spawning enemies, [[[NOTE THAT ENEMY 1 ITSELF IS NOT ADDED TO ENEMIES, 
    #AS IT'S THE SOURCE MATERIAL. THEN, ACTIVEENEMY1 IS ADDED TO IT EACH 
    #TIME BECAUSE IT ACTUALLY DOES STUFF]]]
    def spawnEnemies(self):
        global activeEnemy1
        global enemy1SpawnCount

        for i in range(enemy1SpawnCount):
            activeEnemy1 = enemy1()
            enemies.add(activeEnemy1)
            allSprites.add(activeEnemy1)
            activeEnemy1.rect.left = random.randrange(0,(displayWidth - enemy1Width))
            activeEnemy1.rect.bottom = random.randrange((-enemy1Height*2), 0)
    
    #drawing
    def draw(self,surface):
        surface.blit(self.image,self.rect)

class enemy2(pygame.sprite.Sprite):
    #initialization of source sprite
    def __init__(self):
        super().__init__()

        if secretMode == False:
            self.image = pygame.image.load('enemyShip2.png')
        else:
            self.image = pygame.image.load('altSkins/enemyShip2Alt.png')

        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth *0.5),(displayHeight * -0.2))
    
    #updating only active sprites
    def update(self):
        #grabbing globals
        global eBulletStart
        global enemyShoot

        if (self in enemies) and (self.rect.top < displayHeight * 0.05):
            self.rect.move_ip(0,enemy2Speed)
        
        #basically since this happens so quickly for each enemy it cycles
        #between them, so they're shooting at BASICALLY the same time but technically kinda not
        elif (self in enemies) and (self.rect.top == (displayHeight * 0.05)) and (enemyShoot == True):
            eBulletStart = self.rect.center
            eB1.shoot()
            pygame.mixer.Sound.play(enemyShootSound)
    
    def spawnEnemies(self):
        global activeEnemy2
        global enemy2SpawnCount
        
        for i in range(enemy2SpawnCount):
            activeEnemy2 = enemy2()
            enemies.add(activeEnemy2)
            allSprites.add(activeEnemy2)
            activeEnemy2.rect.left = random.randrange(0,(displayWidth - enemy2Width))
            activeEnemy2.rect.bottom = 0

    def draw(self,surface):
        surface.blit(self.image,self.rect)

class finalBoss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        if secretMode == False:
            self.image = pygame.image.load('finalBoss.png')
        else:
            self.image = pygame.image.load('altSkins/finalBossAlt.png')

        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth *0.5),(displayHeight * -0.5))
    
    def update(self):
        global bossSpeed

        #stops after just passing the top of the screen
        if (self in allSprites) and (self.rect.top < 0):
            self.rect.move_ip(0,bossSpeed)
        
        #shifts sideways to lightly follow player
        if (p1.rect.right < self.rect.center[0]) and (self.rect.left > 0):
            self.rect.move_ip(-bossSpeed,0)
        elif (p1.rect.left > self.rect.center[0]) and (self.rect.right < displayWidth):
            self.rect.move_ip(bossSpeed,0)
    
    def spawn(self):
        global activeBoss
        
        activeBoss = finalBoss()
        allSprites.add(activeBoss)
        enemies.add(activeBoss)
        activeBoss.rect.center = ((displayWidth/2),(-bossHeight/2))

    def draw(self,surface):
        surface.blit(self.image,self.rect)

class powerup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('pierceUp.png')
        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth *0.5),(displayHeight * -0.5))
    
    def spawn(self):
        global powerupWidth
        global powerupHeight
        global powerupType
        global playerShootCooldown
        global powerupColor
        
        #makes itself one of the three types at random, but not firerate if firerate is literally once per frame as to not break things
        if (playerShootCooldown != 1):
            type = random.randint(0,2)
        else:
            type = random.randint(1,2)

        if (type == 0):
            
            if secretMode == False:
                self.image = pygame.image.load('firerateUp.png')
            else:
                self.image = pygame.image.load('altSkins/powerupAlt.png')
            
            powerupType = "Firerate"
        elif (type == 1):
            
            if secretMode == False:
                self.image = pygame.image.load('pierceUp.png')
            else:
                self.image = pygame.image.load('altSkins/powerupAlt.png')

            powerupType = "Pierce"
        else:
            
            if secretMode == False:
                self.image = pygame.image.load('speedUp.png')
            else:
                self.image = pygame.image.load('altSkins/powerupAlt.png')

            powerupType = "Speed"

        #goes somewhere in bounds, but not the very top of the screen
        self.rect.left = random.randint(0,(displayWidth - powerupWidth))
        self.rect.top = random.randint((400),(displayHeight - powerupHeight))

        #moves again if touching player
        while pygame.sprite.collide_rect(p1,self):
            self.rect.left = random.randint(0,(displayWidth - powerupWidth))
            self.rect.top = random.randint((400),(displayHeight - powerupHeight))
    
    def collect(self):
        global powerupType
        global playerSpeed
        global playerShootCooldown
        global playerCanShoot
        global powerupCanDisplay
        global powerupColor
        global powerupDisplayType

        powerupCanDisplay = True

        #does different things based on the type of powerup it is
            #pierce makes you pierce one more enemy, speed increases speed by 2, firerate reduces required cooldown total for shooting by 1 frame
        if (powerupType == "Firerate"):
            playerShootCooldown -= 1
            playerCanShoot = playerShootCooldown
            powerupDisplayType = "Firerate"
            
            if secretMode == False:
                powerupColor = redder
            else: powerupColor = greener

        elif (powerupType == "Pierce"):
            playerBullet.pBulletPierce += 1
            powerupDisplayType = "Pierce"
            if secretMode == False:
                powerupColor = bluer
            else: 
                powerupColor = greener

        else:
            playerSpeed += 2
            powerupDisplayType = "Speed"
            powerupColor = greener
        
        #text goes away after 5 seconds
        pygame.time.set_timer(powerupTextEnd,5000,0)

        #noise
        pygame.mixer.Sound.play(powerupSound)

        #goes back to the ether
        self.rect.center = (displayWidth/2,-displayHeight/2)

    def draw(self,surface):
        surface.blit(self.image,self.rect)

class background(pygame.sprite.Sprite):
    #initialization
    def __init__(self):
        super().__init__()
        if secretMode == False:
                self.image = pygame.image.load('spaceBG.png')
        else:
                self.image = pygame.image.load('altSkins/spaceBGAlt.png')
        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth * 0.5),(displayHeight * 0.5))
    
    #drawing
    def draw(self,surface):
        surface.blit(self.image,self.rect)

class introBackground(pygame.sprite.Sprite):
    #initialization
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('introBG.png')
        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth * 0.5),(displayHeight * 0.5))
    
    #drawing
    def draw(self,surface):
        surface.blit(self.image,self.rect)

class hitIndicator(pygame.sprite.Sprite):
    #initialize
    def __init__(self):
        super().__init__()
        if secretMode == False:
                self.image = pygame.image.load('bulletHit.png')
        else:
                self.image = pygame.image.load('altSkins/bulletHitAlt.png')
        self.rect = self.image.get_rect()
        self.rect.center = ((displayWidth * 0.5),(displayHeight * 0.5))
    
    def showHit(self):
        global bulletHitSpot
        global activeHI
        global hitIndicators
        
        activeHI = hitIndicator()
        hitIndicators.add(activeHI)

        #moves activeHI to center because of script in each collision
        activeHI.rect.center = bulletHitSpot

        #kills in .2 seconds, see the event collection
        pygame.time.set_timer(hIKill,200,0)



    def draw(self,surface):
        surface.blit(self.image,self.rect)

#setting up sprites and groups
p1 = player()
pB1 = playerBullet()
eB1 = enemyBullet()
e1 = enemy1()
e2 = enemy2()
fB = finalBoss()
bG1 = background()
bG2 = introBackground()
bL = bossLaser()
hI = hitIndicator()
pU = powerup()

activeEnemy1 = enemy1()
activeEnemy2 = enemy2()
activePlayerBullet = playerBullet()
activeEnemyBullet = enemyBullet()
activeBoss = finalBoss()
activeLaser = bossLaser()
activeHI = hitIndicator()

#these groups are for ACTIVE SPRITES, NOT SOURCE SPRITES
enemies = pygame.sprite.Group()
enemyProjectiles = pygame.sprite.Group()
playerProjectiles = pygame.sprite.Group()
hitIndicators = pygame.sprite.Group()
powerups = pygame.sprite.Group()

powerups.add(pU)

allSprites = pygame.sprite.Group()
allSprites.add(p1, enemies, playerProjectiles)

#a bunch of functions
def scoreDisplay(count):
    font = pygame.font.SysFont(None, 40)
    text = font.render("Score: " + str(count), True, white)
    gameDisplay.blit(text,(0,0))

def powerupDisplay(text,col):
    font = pygame.font.SysFont(None, 40)
    text = font.render(str(text + " up!"), True, col)
    gameDisplay.blit(text,(0,40))

def textObjects(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()

def messageDisplay(text,sleepyTime=None):
    largeText = pygame.font.Font(gameFont,115)
    TextSurf,TextRect = textObjects(text, largeText)
    TextRect.center = ((displayWidth/2),(displayHeight/2))
    gameDisplay.blit(TextSurf, TextRect)
    
    pygame.display.update()
    if (sleepyTime != None):
        time.sleep(sleepyTime)

def button(text,x,y,width,height,color1,color2,action=None):
    #getting mouse coords and click
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    #drawing the button in each color if mouse is or isn't hovering
    if (x+width > mouse[0] > x) and (y+height > mouse[1] > y):
        pygame.draw.rect(gameDisplay,color2,(x,y,width,height))

        if (click[0] == 1) and (action != None):
            action()
    else:
        pygame.draw.rect(gameDisplay,color1,(x,y,width,height))
    
    #text for the button specifically
    smallText = pygame.font.Font(gameFont,20)
    textSurf, textRect = textObjects(text,smallText)
    textRect.center = ((x+(width/2)),(y+(height/2)))
    gameDisplay.blit(textSurf,textRect)

def gameQuit():
    pygame.quit()
    quit()

def unpause():
    global pause
    pause = False
    
    #unquiets music
    pygame.mixer.music.set_volume(1.0)

def classicStart():
    global gameMode
    global gameReset

    gameMode = "classic"
    gameReset = False
    THELOOP()

def endlessStart():
    global gameMode
    global gameReset

    gameMode = "endless"
    gameReset = False
    THELOOP()

def resetGame():
    global gameReset
    global pause
    global gameOver
    global gameWin

    #resets the main LOOPVARIABLES^tm so it should go back to title screen
    gameReset = True

    pause = False
    gameOver = False
    gameWin = False

    #stops music for title screen and puts volume to proper amount
    pygame.mixer.music.pause()
    pygame.mixer.music.set_volume(1)

def updateScreen(tick):
    pygame.display.update()
    clock.tick(tick)

#the BIG LOOPS (different screens throughout the game)
def PAUSELOOP():
    #creating and calling to global variable so that it also works with unpause()
    global pause
    pause = True

    messageDisplay("Game Paused")

    #button dimensions
    pButtonW = 200
    pButtonH = 100

    #quieting music
    pygame.mixer.music.set_volume(0.3)

    #main body of the actual pause
    while (pause):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameQuit()
        
        button("Continue", (displayWidth/3 - pButtonW),(displayHeight * 0.7),pButtonW,pButtonH,green,greener,unpause)
        button("Main Menu", (2 * displayWidth/3), (displayHeight * 0.7), pButtonW, pButtonH, red, redder,resetGame)

        updateScreen(15)

def INTROLOOP():
    global gameName
    global secretMode
    
    #button dimensions
    inButtonW = 200
    inButtonH = 100
    
    #one second delay so coming back to it doesn't break and stuff
    bG2.__init__()
    messageDisplay(gameName,1)
    gameDisplay.fill(black)
    
    #main body of the loop
    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                gameQuit()
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_BACKSLASH):
                    if secretMode == False:
                        secretMode = True
                    else:
                        secretMode = False
                    pygame.mixer.Sound.play(secretSound)

        #everything being drawn
        bG2.draw(gameDisplay)
        button("Classic Mode",(displayWidth*5/6 - inButtonW/4),(displayHeight/5),inButtonW,inButtonH,green,greener,classicStart)
        button("Endless Mode",(displayWidth*5/6 - inButtonW/4),(displayHeight/2 - inButtonH/2),inButtonW,inButtonH,blue,bluer,endlessStart)
        button("Quit",(displayWidth*5/6 - inButtonW/4),(displayHeight*4/5 - inButtonH),inButtonW,inButtonH,red,redder,gameQuit)
        
        #stuff updating
        updateScreen(15)

def GAMEOVERLOOP():
    global gameOver

    #sound plays and music pauses
    pygame.mixer.Sound.play(gameOverSound)
    pygame.mixer.music.stop()

    #pauses for 1 second
    messageDisplay('GAME OVER',1)

    #button dimensions
    pButtonW = 200
    pButtonH = 100

    gameOver = True
    
    #main game over loop
    while gameOver == True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                gameQuit()
        
        button("Main Menu", (displayWidth/3 - pButtonW),(displayHeight * 0.7),pButtonW,pButtonH,green,greener,resetGame)
        button("Quit Game", (2 * displayWidth/3), (displayHeight * 0.7), pButtonW, pButtonH, red, redder, gameQuit)

        updateScreen(15)

def WINLOOP():
    global gameWin
    global gameReset

    #button dimensions
    inButtonW = 200
    inButtonH = 100
    
    gameWin = True
    gameReset = True

    #pause music when it comes up
    pygame.mixer.music.pause()
    pygame.mixer.Sound.play(winGameSound)

    #main body of the loop
    while (gameWin == True):
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                gameQuit()

        #everything being drawn
        button("Main Menu", (displayWidth/3 - inButtonW),(displayHeight * 0.7),inButtonW,inButtonH,green,greener,resetGame)
        button("Quit", (2 * displayWidth/3), (displayHeight * 0.7), inButtonW, inButtonH, red, redder, gameQuit)
        messageDisplay("YOU WIN!")

        #stuff updating
        updateScreen(15)

def THELOOP():
    #accessing global variables
    global score
    global enemies
    global enemy1SpawnCount
    global enemy2SpawnCount
    global enemyShoot
    global playerCanShoot
    global bulletHitSpot
    global activeHI
    global playerShootCooldown
    global pBulletPierce
    global playerSpeed
    global gameReset
    global powerupCanDisplay
    global powerupType
    global powerupColor
    global powerupDisplayType
    global bossStage

    #initializing stuff and resetting values
    p1.__init__()
    
    pB1.__init__()
    eB1.__init__()

    e1.__init__()
    e2.__init__()

    bG1.__init__()

    hI.__init__()

    score = 0
    enemy1SpawnCount = 3
    enemy2SpawnCount = 2

    playerShootCooldown = 7
    playerCanShoot = playerShootCooldown
    pBulletPierce = 0
    playerSpeed = 10

    bossStage = False

    powerupCanDisplay = False

    pygame.time.set_timer(scoreIncrease,1000)

    #music starts
    pygame.mixer.music.load('BGMusic.mp3')
    pygame.mixer.music.play(-1)

    #cleaning up stuff as necessary
    for i in enemies:
        i.kill()
    for i in enemyProjectiles:
        i.kill()
    for i in playerProjectiles:
        i.kill()
    for i in hitIndicators:
        i.kill()

    #THE CORE OF THE LOOP
    while gameReset == False:
        #turning enemyShoot off so enemies don't shoot repeatedly
        enemyShoot = False
        
        #charges up player shooting to be able to shoot 6 times/sec
        if (playerCanShoot != playerShootCooldown):
            playerCanShoot += 1

        #checking for and doing events
        for event in pygame.event.get():
            
            #quitting
            if (event.type == pygame.QUIT):
                gameQuit()
            
            #certain, more "universal" player controls
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    PAUSELOOP()
                if (event.key == pygame.K_SPACE) and (playerCanShoot == playerShootCooldown):
                    pygame.mixer.Sound.play(playerShootSound)
                    pB1.shoot()
                    playerCanShoot = 0
            
            #hitIndicator killing
            if (event.type == hIKill):
                for i in hitIndicators:
                    i.kill()

            #ending powerupDisplay
            if (event.type == powerupTextEnd):
                powerupCanDisplay = False
            
            #a bunch of things that happen at certain score intervals (all spawns, spawnCount increases, enemy shoot, and BOSSLOOP())
            if (event.type == scoreIncrease):
                score += 1
                if (score % 3 == 0):
                    e1.spawnEnemies()
                if (score % 12 == 0):
                    enemy1SpawnCount += 1
                if (score % 10 == 0):
                    e2.spawnEnemies()
                    
                    #just a quick check to not spawn powerup at 100 score in classic mode to avoid jank
                    if (score != 0) and ((score != 100) or (gameMode == "endless")):
                        pU.spawn()

                if (score % 20 == 0):
                    enemy2SpawnCount += 1
                if (score % 4 == 0):
                    enemyShoot = True
                if (score == 100) and (gameMode == "classic"):
                    BOSSLOOP()

        #updating all sprites, duh
        allSprites.update()

        #passive enemy1 movement
        for i in enemies:
            if (i == enemy1()):
                e1.drift()

        #drawing stuff
        bG1.draw(gameDisplay)
        
        enemyProjectiles.draw(gameDisplay)
        playerProjectiles.draw(gameDisplay)
        p1.draw(gameDisplay)

        pU.draw(gameDisplay)

        enemies.draw(gameDisplay)

        hitIndicators.draw(gameDisplay)

        scoreDisplay(score)
        
        #collision detections
        if (pygame.sprite.spritecollideany(p1,enemies) or pygame.sprite.spritecollideany(p1,enemyProjectiles)) and (bossStage == False):
            #checks mask collision specifically
            if pygame.sprite.spritecollideany(p1,enemies,pygame.sprite.collide_mask) or pygame.sprite.spritecollideany(p1,enemyProjectiles,pygame.sprite.collide_mask):
                #indicator
                bulletHitSpot = p1.rect.center
                hI.showHit()
                activeHI.draw(gameDisplay)

                #noise + game over
                pygame.mixer.Sound.play(playerCrashSound)
                GAMEOVERLOOP()
        
        if pygame.sprite.spritecollide(p1,powerups,0):
            pU.collect()
        
        #only displays powerup text briefly after pickup, done after collection so text displays properly
        if (powerupCanDisplay == True):
            powerupDisplay(powerupDisplayType,powerupColor)

        #whole thing updates
        updateScreen(30)

def BOSSLOOP():
    #accessing global variables
    global score
    global activeBoss
    global playerCanShoot
    global bossHealth
    global eBulletStart
    global bulletHitSpot
    global activeHI
    global playerShootCooldown
    global gameReset
    global bossStage

    #initializing boss
    fB.__init__()

    bossHealth = 100

    bossStage = True

    #boss music starts
    pygame.mixer.music.load('bossMusic.mp3')
    pygame.mixer.music.play(-1)

    #clearing stuff
    for i in enemies:
        i.kill()
    for i in enemyProjectiles:
        i.kill()
    for i in playerProjectiles:
        i.kill()
    
    fB.spawn()

    pygame.time.set_timer(bossShoot,850)

    #THE CORE OF THE LOOP
    while gameReset == False:
        #charges up player shooting to be able to shoot 6 times/sec
        if (playerCanShoot != playerShootCooldown):
            playerCanShoot += 1

        #checking events
        for event in pygame.event.get():
            
            #quitting
            if (event.type == pygame.QUIT):
                gameQuit()
            
            #certain, more "universal" player controls
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    PAUSELOOP()
                if (event.key == pygame.K_SPACE) and (playerCanShoot == playerShootCooldown):
                    pygame.mixer.Sound.play(playerShootSound)
                    pB1.shoot()
                    playerCanShoot = 0
            
            #hitIndicator killing
            if (event.type == hIKill):
                for i in hitIndicators:
                    i.kill()
            
            if (event.type == bossShoot):
                eBulletStart = ((activeBoss.rect.left + random.randint(60, bossWidth - 60)),(activeBoss.rect.top + random.randint(0,bossHeight - 60)))
                eB1.shoot()

        #updating all sprites, duh
        allSprites.update()

        #drawing stuff
        bG1.draw(gameDisplay)
        
        enemyProjectiles.draw(gameDisplay)
        playerProjectiles.draw(gameDisplay)
        p1.draw(gameDisplay)

        enemies.draw(gameDisplay)

        hitIndicators.draw(gameDisplay)

        scoreDisplay(score)
        
        #collision detections
        if pygame.sprite.spritecollide(p1,enemies,0) or pygame.sprite.spritecollideany(p1,enemyProjectiles):
            
            #checks mask specifically
            if pygame.sprite.spritecollideany(p1,enemies,pygame.sprite.collide_mask) or pygame.sprite.spritecollideany(p1,enemyProjectiles,pygame.sprite.collide_mask):
                bulletHitSpot = p1.rect.center
                hI.showHit()
                activeHI.draw(gameDisplay)
                
                pygame.mixer.Sound.play(playerCrashSound)
                GAMEOVERLOOP()
        
        #boss loses health instead of enemy dying loop
        for i in playerProjectiles:
            if pygame.sprite.spritecollide(i,enemies,0):

                #mask specifically
                if pygame.sprite.spritecollide(i,enemies,0,pygame.sprite.collide_mask):
                    bulletHitSpot = i.rect.midtop
                    hI.showHit()
                    
                    i.kill()
                    bossHealth -= 1

                    #boss fires laser at 75, 50, and 25 hp
                    if (bossHealth % 25 == 0) and (bossHealth > 0):
                        pygame.mixer.Sound.play(laserChargeSound)
                        eBulletStart = (activeBoss.rect.center[0],(-laserHeight * 3))
                        bL.shoot()
                    else:
                        pygame.mixer.Sound.play(enemyCrashSound)

            #this is like a mini loop, it's just the death animation and then WINLOOP() tho
            if (bossHealth == 0) or (bossHealth < 0):
                for i in range(30):
                    bulletHitSpot = ((random.randint(activeBoss.rect.left,activeBoss.rect.right)),(random.randint(activeBoss.rect.top,activeBoss.rect.bottom)))
                    hI.showHit()
                    pygame.time.wait(100)
                    hitIndicators.draw(gameDisplay)
                    pygame.mixer.Sound.play(enemyCrashSound)
                    
                    updateScreen(30)
                
                for i in hitIndicators:
                    i.kill()
                activeBoss.kill()

                pygame.time.wait(100)

                bG1.draw(gameDisplay)
                p1.draw(gameDisplay)

                pygame.display.update()
                
                WINLOOP()

        #whole thing updates
        updateScreen(30)
        
#actual cycle itself
INTROLOOP()
gameQuit()