import pygame
import pygame_gui

pygame.init()

HEIGHT, WIDTH = 720, 1280
HUD_PADDING = 5

BUTTON_WIDTH = 0.2*WIDTH - 2*HUD_PADDING
BUTTON_HEIGHT = 50

pygame.display.set_caption("Map Creator")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((WIDTH, HEIGHT))


# map editor
container = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((HUD_PADDING, HUD_PADDING), (0.2*WIDTH, HEIGHT - 2*HUD_PADDING)),
                                        starting_height=1,
                                        manager=manager,
                                        object_id="#container",
                                )
add_spawn_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0), (BUTTON_WIDTH, BUTTON_HEIGHT)),
                                               text="Dodaj dom",
                                               manager=manager,
                                               container=container,)
add_hospital_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, BUTTON_HEIGHT), (BUTTON_WIDTH, BUTTON_HEIGHT)),
                                                   text="Dodaj szpital",
                                                   manager=manager,
                                                   container=container)


# element editor
editor = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((WIDTH - 0.2*WIDTH - HUD_PADDING, HUD_PADDING), (0.2*WIDTH, 0.2*HEIGHT - 2*HUD_PADDING)),
                                        starting_height=1,
                                        manager=manager,
                                        object_id="#editor",
                                )
editor_label = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 10), (100, 20)),
                                                    manager=manager,
                                                    container=editor,
                                                    object_id="#editor_label",
                                                    initial_text="Pojemność")
exit_editor_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0.2*WIDTH - 25, 10), (20, 20)),
                                                    manager=manager,
                                                    container=editor,
                                                    text="X")
editor_text_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 30), (140, 20)),
                                                        manager=manager,
                                                        container=editor,
                                                        object_id="#editor_text_input",
                                                        initial_text="")



# data
houses = []
hospitals = []
paths = []

# ui helper variables
dragging = False
dragged_house = None
running = True
path_drawing_mode = False

path = []
start_point = True
end_point = False
editor.hide()
selected_building = None

while running:
    time_delta = clock.tick(60)/1000.0
    screen.fill((57, 200, 20))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # exit
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN: # dragging element event
            for house in houses + hospitals:
                if house.collidepoint(event.pos):
                    selected_building = house
                    editor.show()
                    break
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_h: # hide/show hud
                if container.visible:
                    container.hide()
                else:
                    container.show()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                if path_drawing_mode:
                    print("Drawing lines mode")
                else:
                    print("Exited drawing lines mode")
                path_drawing_mode = not path_drawing_mode
        if event.type == pygame_gui.UI_BUTTON_PRESSED: 
            if event.ui_element == add_spawn_button:
                houses.append(pygame.Rect((WIDTH // 2, HEIGHT // 2), (40, 40))) # add spawnpoint button event
            if event.ui_element == add_hospital_button:
                hospitals.append(pygame.Rect((WIDTH // 2, HEIGHT // 2), (40, 40))) # add hospital button event
            if event.ui_element == exit_editor_button:
                editor.hide()
                selected_building = None
        if event.type == pygame.MOUSEBUTTONDOWN and not path_drawing_mode: # dragging element event
            for house in houses + hospitals:
                if house.collidepoint(event.pos):
                    dragging = True
                    offset_x = house.x - event.pos[0]
                    offset_y = house.y - event.pos[1]
                    dragged_house = house
                    break
        if event.type == pygame.MOUSEBUTTONUP and not path_drawing_mode: # stop dragging element event
            dragging = False
            dragged_house = None
        if event.type == pygame.MOUSEMOTION: # move element
            if dragging and dragged_house:
                dragged_house.x = event.pos[0] + offset_x
                dragged_house.y = event.pos[1] + offset_y
        if event.type == pygame.MOUSEBUTTONDOWN and path_drawing_mode: # draw path
            mouse_pos = pygame.mouse.get_pos()
            if any(house.collidepoint(mouse_pos) for house in houses + hospitals) and start_point:
                path.append(mouse_pos)
                start_point = False
                end_point = True
            elif any(house.collidepoint(mouse_pos) for house in houses + hospitals) and end_point:
                path_drawing_mode = not path_drawing_mode
                path.append(mouse_pos)
                paths.append(path)
                path = []
                start_point = True
                end_point = False
            elif not start_point:
                path.append(mouse_pos)

            
        manager.process_events(event)
    manager.update(time_delta)  
    
    for house in houses:
        pygame.draw.rect(screen, "blue", house) 
    for hospital in hospitals:
        pygame.draw.rect(screen, "red", hospital)
    for p in paths:
        if len(p) > 1:
            pygame.draw.lines(screen, "black", False, p, 4)
        

    manager.draw_ui(screen)
    pygame.display.flip() # update display

    clock.tick(60)

pygame.quit()