import json
import os
import random
import sys
import pygame
from PIL import Image, ImageSequence
from src.collectibles import Ring, Signpost
from src.enemies import Obstacle
from src.player import Player


def resource_path(relative_path):
    """Retorna o caminho absoluto tanto em desenvolvimento quanto no executável PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

WIDTH = 1280
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sonic Race Remastered")

# --- DICIONÁRIO DE IDIOMAS (LOCALIZATION) ---
LANG_DATA = {
    "PT": {
        "start_prompt": "[ ESPAÇO ] Iniciar   |   [ H ] Como Jogar   |   [ L ] Idioma: PT",
        "top_title": "TOP 3 RECORDES",
        "how_title": "COMO JOGAR",
        "how_back": "Pressione [ ESC ] ou [ ESPAÇO ] para Voltar ao Menu",
        "paused_title": "JOGO PAUSADO",
        "paused_opts": "[ESC] Continuar   |   [R] Reiniciar   |   [M] Menu",
        "gameover_title": "GAME OVER",
        "score_label": "PONTUAÇÃO",
        "name_prompt_go": "DIGITE SUAS INICIAIS (3 LETRAS):",
        "opts_go": "[ENTER] Salvar   |   [R] Reiniciar",
        "victory_title": "SONIC CLEARED THE ACT!",
        "rings_bonus": "BÔNUS DE ANÉIS",
        "total_label": "TOTAL",
        "name_prompt_vic": "INSIRA SEU NOME PARA O HALL DA FAMA:",
        "opts_vic": "[ENTER] Confirmar   |   [R] Jogar Novamente",
        "instructions": [
            ("[ESPAÇO] / [W] / [SETA CIMA]", "Pular (Segure para pular mais alto)"),
            ("[S] / [SETA BAIXO]", "Abaixar para desviar de inimigos voadores"),
            ("ATAQUE GIRATÓRIO", "Pule em cima dos Badniks para destruí-los (+100 pts)"),
            ("ANÉIS DOURADOS", "Protegem você contra 1 dano. Colete para pontuar!"),
            ("[ESC] / [P]", "Pausar a partida / Acessar opções a qualquer momento"),
            ("META FINAL", "Alcance 10.000 pontos para cruzar a placa e vencer!"),
        ],
    },
    "EN": {
        "start_prompt": "[ SPACE ] Start Game   |   [ H ] How to Play   |   [ L ] Lang: EN",
        "top_title": "TOP 3 HIGH SCORES",
        "how_title": "HOW TO PLAY",
        "how_back": "Press [ ESC ] or [ SPACE ] to Return to Menu",
        "paused_title": "GAME PAUSED",
        "paused_opts": "[ESC] Resume   |   [R] Restart   |   [M] Menu",
        "gameover_title": "GAME OVER",
        "score_label": "SCORE",
        "name_prompt_go": "ENTER YOUR INITIALS (3 LETTERS):",
        "opts_go": "[ENTER] Save   |   [R] Restart",
        "victory_title": "SONIC CLEARED THE ACT!",
        "rings_bonus": "RING BONUS",
        "total_label": "TOTAL",
        "name_prompt_vic": "ENTER YOUR NAME FOR THE HALL OF FAME:",
        "opts_vic": "[ENTER] Confirm   |   [R] Play Again",
        "instructions": [
            ("[SPACE] / [W] / [UP ARROW]", "Jump (Hold to jump higher)"),
            ("[S] / [DOWN ARROW]", "Crouch / Duck to dodge flying enemies"),
            ("SPIN ATTACK", "Jump on Badniks to destroy them (+100 pts)"),
            ("GOLDEN RINGS", "Protect you from 1 hit. Collect for points!"),
            ("[ESC] / [P]", "Pause the game / Access options anytime"),
            ("GOAL", "Reach 10,000 points to cross the signpost & win!"),
        ],
    },
}

# --- ÁUDIOS ---
sound_dir = resource_path(os.path.join("assets", "sounds"))
path_opening = os.path.join(sound_dir, "Sonic_opening_theme.mp3")
path_stage = os.path.join(sound_dir, "song_sonic.mp3")
path_gameover = os.path.join(sound_dir, "Sonic_Game_Over.mp3")
path_victory = os.path.join(sound_dir, "Sonic-victory-theme.mp3")
path_jump = os.path.join(sound_dir, "Sonic-Jump-Sound.mp3")
path_ring = os.path.join(sound_dir, "Sonic-Ring-Sound.mp3")

path_loss = None
if os.path.exists(sound_dir):
    for f in os.listdir(sound_dir):
        if "losing-rings" in f.lower():
            path_loss = os.path.join(sound_dir, f)
            break

snd_jump = None
if os.path.exists(path_jump):
    try:
        snd_jump = pygame.mixer.Sound(path_jump)
        snd_jump.set_volume(0.6)
    except Exception:
        pass

snd_ring = None
if os.path.exists(path_ring):
    try:
        snd_ring = pygame.mixer.Sound(path_ring)
        snd_ring.set_volume(0.7)
    except Exception:
        pass

snd_loss = None
if path_loss and os.path.exists(path_loss):
    try:
        snd_loss = pygame.mixer.Sound(path_loss)
        snd_loss.set_volume(0.7)
    except Exception:
        pass


def play_music(path, loop=-1, volume=0.5):
    if path and os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loop)
        except Exception:
            pass


play_music(path_opening, loop=-1, volume=0.6)

# --- SISTEMA DE RECORDE E CONFIGURAÇÃO ---
SAVE_PATH = os.path.join("data", "save.json")


def load_save_data():
    default_scores = [
        {"name": "SON", "score": 5000},
        {"name": "TAI", "score": 3000},
        {"name": "KNU", "score": 1500},
    ]
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r") as f:
                data = json.load(f)
                return data.get("top_scores", default_scores), data.get("lang", "PT")
        except Exception:
            pass
    return default_scores, "PT"


def save_score(new_score, name, lang):
    os.makedirs("data", exist_ok=True)
    scores, _ = load_save_data()
    valid_name = name.strip().upper()[:3] or "AAA"

    scores.append({"name": valid_name, "score": new_score})
    scores.sort(key=lambda x: x["score"], reverse=True)
    top_3 = scores[:3]

    with open(SAVE_PATH, "w") as f:
        json.dump({"top_scores": top_3, "lang": lang}, f, indent=4)


def save_lang_pref(lang):
    os.makedirs("data", exist_ok=True)
    scores, _ = load_save_data()
    with open(SAVE_PATH, "w") as f:
        json.dump({"top_scores": scores, "lang": lang}, f, indent=4)


_, current_lang = load_save_data()

menu_gif_path = resource_path(os.path.join("assets", "img", "destaque_sonic.gif"))
menu_frames = []
if os.path.exists(menu_gif_path):
    try:
        pil_menu = Image.open(menu_gif_path)
        for frame in ImageSequence.Iterator(pil_menu):
            frame_rgba = frame.convert("RGBA")
            surf = pygame.image.fromstring(frame_rgba.tobytes(), frame_rgba.size, "RGBA")
            surf = pygame.transform.scale(surf, (540, 310))
            menu_frames.append(surf)
    except Exception:
        pass

img_dir = resource_path(os.path.join("assets", "img"))
available_files = os.listdir(img_dir) if os.path.exists(img_dir) else []
bg_files = [
    f for f in available_files
    if ("background" in f.lower() or "green_hill" in f.lower()) and f.endswith((".png", ".jpg"))
]

bgs = []
for bg_name in sorted(bg_files):
    full_path = os.path.join(img_dir, bg_name)
    try:
        surf = pygame.image.load(full_path).convert()
        surf = pygame.transform.scale(surf, (WIDTH, HEIGHT))
        bgs.append(surf)
    except Exception:
        pass

# Garante fallback se nenhum background carregar (evita divisão por zero)
if not bgs:
    fallback_surf = pygame.Surface((WIDTH, HEIGHT))
    fallback_surf.fill((20, 30, 70))
    bgs = [fallback_surf, fallback_surf]
elif len(bgs) == 1:
    bgs.append(bgs[0])

current_bg_idx = 0
next_bg_idx = 1 if len(bgs) > 1 else 0
bg_x_far = 0

is_transitioning = False
transition_alpha = 0.0
fade_speed = 0.5

clock = pygame.time.Clock()
font_hud = pygame.font.SysFont("Arial", 26, bold=True)
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_arcade = pygame.font.SysFont("Courier New", 68, bold=True)
font_small = pygame.font.SysFont("Arial", 18, bold=True)

state = "MENU"
menu_frame_idx = 0.0

input_name = ""
cursor_timer = 0

player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

obstacles_group = pygame.sprite.Group()
rings_group = pygame.sprite.Group()
signpost_group = pygame.sprite.Group()

base_speed = 13.0
max_speed = 34.0
speed_increment = 0.0035

score = 0
BG_CHANGE_INTERVAL = 3000
next_bg_score_target = BG_CHANGE_INTERVAL
VICTORY_SCORE = 10000
signpost_spawned = False

enemy_timer = 0
ring_timer = 0

running = True


def reset_game():
    global player, all_sprites, obstacles_group, rings_group, signpost_group
    global base_speed, score, next_bg_score_target, current_bg_idx, next_bg_idx
    global is_transitioning, transition_alpha, signpost_spawned, state, enemy_timer, ring_timer, input_name
    base_speed = 13.0
    score = 0
    enemy_timer = 0
    ring_timer = 0
    input_name = ""
    next_bg_score_target = BG_CHANGE_INTERVAL
    current_bg_idx = 0
    total_bgs = max(1, len(bgs))
    next_bg_idx = 1 % total_bgs
    is_transitioning = False
    transition_alpha = 0.0
    signpost_spawned = False

    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    obstacles_group.empty()
    rings_group.empty()
    signpost_group.empty()
    state = "PLAYING"

    play_music(path_stage, loop=-1, volume=0.5)


while running:
    clock.tick(60)
    cursor_timer += 1
    T = LANG_DATA[current_lang]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == "MENU":
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    reset_game()
                elif event.key in (pygame.K_h, pygame.K_c):
                    state = "HOW_TO_PLAY"
                elif event.key == pygame.K_l:
                    current_lang = "EN" if current_lang == "PT" else "PT"
                    save_lang_pref(current_lang)

            elif state == "HOW_TO_PLAY":
                if event.key in (
                    pygame.K_ESCAPE,
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                    pygame.K_h,
                    pygame.K_c,
                ):
                    state = "MENU"

            elif state == "PLAYING":
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if not player.is_jumping and not player.is_ducking and snd_jump:
                        snd_jump.play()
                    player.jump()
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    player.duck()
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    state = "PAUSED"
                    pygame.mixer.music.pause()

            elif state == "PAUSED":
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    state = "PLAYING"
                    pygame.mixer.music.unpause()
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_m:
                    state = "MENU"
                    play_music(path_opening, loop=-1, volume=0.6)

            elif state in ("GAMEOVER", "VICTORY"):
                if event.key == pygame.K_BACKSPACE:
                    input_name = input_name[:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    final_score = score + (player.rings * 100) if state == "VICTORY" else score
                    save_score(final_score, input_name or "AAA", current_lang)
                    state = "MENU"
                    play_music(path_opening, loop=-1, volume=0.6)
                elif event.key == pygame.K_r:
                    final_score = score + (player.rings * 100) if state == "VICTORY" else score
                    save_score(final_score, input_name or "AAA", current_lang)
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    state = "MENU"
                    play_music(path_opening, loop=-1, volume=0.6)
                else:
                    if len(input_name) < 3 and event.unicode.isalnum():
                        input_name += event.unicode.upper()

        if event.type == pygame.KEYUP and state == "PLAYING":
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                player.cut_jump()
            if event.key in (pygame.K_DOWN, pygame.K_s):
                player.stand_up()

    # --- LÓGICA DE JOGO ATIVO ---
    if state == "PLAYING":
        if base_speed < max_speed:
            base_speed += speed_increment

        score += 1
        player.animation_speed = min(0.30 + (base_speed * 0.022), 0.90)

        # Transição de Cenário
        if score >= next_bg_score_target and not is_transitioning:
            is_transitioning = True
            transition_alpha = 0.0
            total_bgs = max(1, len(bgs))
            next_bg_idx = (current_bg_idx + 1) % total_bgs
            next_bg_score_target += BG_CHANGE_INTERVAL

        if is_transitioning:
            transition_alpha += fade_speed
            if transition_alpha >= 255:
                transition_alpha = 255
                is_transitioning = False
                current_bg_idx = next_bg_idx

        # Parallax
        bg_x_far -= base_speed * 0.22
        if bg_x_far <= -WIDTH:
            bg_x_far = 0

        # Spawns
        if not signpost_spawned:
            enemy_timer += 1
            spawn_limit = max(42, int(110 - (score / 130)))
            if enemy_timer >= spawn_limit:
                enemy = Obstacle(speed=int(base_speed))
                all_sprites.add(enemy)
                obstacles_group.add(enemy)
                enemy_timer = 0

            ring_timer += 1
            if ring_timer >= 75:
                ring_y = random.choice([520, 610])
                ring = Ring(
                    WIDTH + random.randint(20, 50),
                    ring_y,
                    speed=int(base_speed * 0.95),
                )
                all_sprites.add(ring)
                rings_group.add(ring)
                ring_timer = 0

        # Linha de Chegada
        if score >= VICTORY_SCORE and not signpost_spawned:
            signpost_spawned = True
            sign = Signpost(
                x=WIDTH + 100, ground_y=680, speed=int(base_speed * 0.7)
            )
            all_sprites.add(sign)
            signpost_group.add(sign)

        all_sprites.update()

        # Coleta de Anéis
        ring_hits = pygame.sprite.spritecollide(
            player, rings_group, True, pygame.sprite.collide_mask
        )
        if ring_hits:
            if snd_ring:
                snd_ring.play()
            for _ in ring_hits:
                player.rings += 1
                score += 20

        # Checagem da Placa
        for sign in signpost_group:
            if (
                pygame.sprite.collide_rect(player, sign)
                or sign.rect.centerx <= player.rect.centerx
            ):
                sign.spin()
                play_music(path_victory, loop=0, volume=0.7)
                state = "VICTORY"
                break

        # Combate contra Inimigos
        hits = pygame.sprite.spritecollide(
            player, obstacles_group, False, pygame.sprite.collide_mask
        )
        if hits:
            for hit_obs in hits:
                if player.is_jumping and not player.is_hit:
                    hit_obs.kill()
                    score += 100
                    player.bounce()
                else:
                    if snd_loss:
                        snd_loss.play()
                    died = player.take_hit()
                    if died:
                        play_music(path_gameover, loop=0, volume=0.7)
                        state = "GAMEOVER"
                    else:
                        hit_obs.kill()
                    break

    elif state == "GAMEOVER":
        player.update()

    if state == "MENU":
        screen.fill((10, 20, 60))
        if menu_frames:
            menu_frame_idx = (menu_frame_idx + 0.2) % len(menu_frames)
            current_menu_img = menu_frames[int(menu_frame_idx)]
            screen.blit(
                current_menu_img, (WIDTH // 2 - 270, HEIGHT // 2 - 320)
            )

        title_text = font_large.render("SONIC RACE", True, (255, 215, 0))
        prompt_text = font_hud.render(T["start_prompt"], True, (255, 255, 255))

        screen.blit(
            title_text,
            title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)),
        )
        screen.blit(
            prompt_text,
            prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 75)),
        )

        # Exibição do TOP 3 Placar
        top_scores, _ = load_save_data()
        box_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 + 115, 500, 180)
        pygame.draw.rect(screen, (15, 25, 80), box_rect, border_radius=12)
        pygame.draw.rect(
            screen, (0, 191, 255), box_rect, width=2, border_radius=12
        )

        score_title = font_hud.render(T["top_title"], True, (0, 255, 255))
        screen.blit(
            score_title,
            score_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140)),
        )

        medals = ["1ST", "2ND", "3RD"]
        colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]

        for i, entry in enumerate(top_scores[:3]):
            rank_str = f"{medals[i]}   {entry['name']: <3} ....... {entry['score']:05d} PTS"
            entry_surf = font_hud.render(rank_str, True, colors[i])
            screen.blit(
                entry_surf,
                entry_surf.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 + 180 + (i * 34))
                ),
            )

        version_text = font_small.render(
            f"v1.0.0 | LANG: {current_lang}", True, (120, 140, 180)
        )
        screen.blit(version_text, (20, HEIGHT - 35))

    elif state == "HOW_TO_PLAY":
        screen.fill((15, 20, 35))
        title = font_large.render(T["how_title"], True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 90)))

        y_start = 180
        for key, desc in T["instructions"]:
            k_surf = font_hud.render(key, True, (0, 255, 255))
            d_surf = font_hud.render(f"-  {desc}", True, (255, 255, 255))
            screen.blit(k_surf, (140, y_start))
            screen.blit(d_surf, (540, y_start))
            y_start += 55

        back_text = font_hud.render(T["how_back"], True, (255, 215, 0))
        screen.blit(back_text, back_text.get_rect(center=(WIDTH // 2, 630)))

    else:
        active_bg = bgs[current_bg_idx]
        screen.blit(active_bg, (int(bg_x_far), 0))
        screen.blit(active_bg, (int(bg_x_far) + WIDTH, 0))

        if is_transitioning:
            fading_bg = bgs[next_bg_idx].copy()
            fading_bg.set_alpha(int(transition_alpha))
            screen.blit(fading_bg, (int(bg_x_far), 0))
            screen.blit(fading_bg, (int(bg_x_far) + WIDTH, 0))

        if (
            player.invincible_timer > 0
            and (player.invincible_timer // 6) % 2 == 0
            and state != "GAMEOVER"
        ):
            pass
        else:
            all_sprites.draw(screen)

        # HUD
        score_text = font_hud.render(
            f"SCORE: {score:05d}", True, (255, 255, 255)
        )
        speed_text = font_hud.render(
            f"SPEED: {int(base_speed * 14)} km/h", True, (255, 215, 0)
        )
        rings_text = font_hud.render(
            f"RINGS: {player.rings:02d}", True, (255, 220, 0)
        )

        screen.blit(score_text, (30, 20))
        screen.blit(speed_text, (30, 55))
        screen.blit(rings_text, (30, 90))

        if state == "PAUSED":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            p_text = font_large.render(T["paused_title"], True, (255, 255, 255))
            opt_text = font_hud.render(
                T["paused_opts"], True, (200, 200, 200)
            )
            screen.blit(
                p_text, p_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            )
            screen.blit(
                opt_text,
                opt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 45)),
            )

        elif state == "GAMEOVER":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            go_text = font_large.render(
                T["gameover_title"], True, (255, 50, 50)
            )
            score_final_text = font_hud.render(
                f"{T['score_label']}: {score:05d}", True, (255, 255, 255)
            )
            name_prompt = font_hud.render(
                T["name_prompt_go"], True, (255, 215, 0)
            )

            display_name = input_name + (
                "_" if (cursor_timer // 20) % 2 == 0 and len(input_name) < 3 else ""
            )
            arcade_name_surf = font_arcade.render(
                f"[ {display_name: <3} ]", True, (0, 255, 255)
            )
            opt_text = font_hud.render(T["opts_go"], True, (200, 200, 200))

            screen.blit(
                go_text,
                go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)),
            )
            screen.blit(
                score_final_text,
                score_final_text.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 - 60)
                ),
            )
            screen.blit(
                name_prompt,
                name_prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 15)),
            )
            screen.blit(
                arcade_name_surf,
                arcade_name_surf.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 + 50)
                ),
            )
            screen.blit(
                opt_text,
                opt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 125)),
            )

        elif state == "VICTORY":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            vic_text = font_large.render(
                T["victory_title"], True, (255, 215, 0)
            )
            total_bonus = score + (player.rings * 100)
            bonus_text = font_hud.render(
                f"{T['rings_bonus']}: {player.rings * 100}   |   {T['total_label']}: {total_bonus}",
                True,
                (255, 255, 255),
            )
            name_prompt = font_hud.render(
                T["name_prompt_vic"], True, (255, 215, 0)
            )

            display_name = input_name + (
                "_" if (cursor_timer // 20) % 2 == 0 and len(input_name) < 3 else ""
            )
            arcade_name_surf = font_arcade.render(
                f"[ {display_name: <3} ]", True, (50, 205, 50)
            )
            opt_text = font_hud.render(T["opts_vic"], True, (200, 200, 200))

            screen.blit(
                vic_text,
                vic_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 130)),
            )
            screen.blit(
                bonus_text,
                bonus_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)),
            )
            screen.blit(
                name_prompt,
                name_prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)),
            )
            screen.blit(
                arcade_name_surf,
                arcade_name_surf.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 + 45)
                ),
            )
            screen.blit(
                opt_text,
                opt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120)),
            )

    pygame.display.flip()

pygame.quit()
sys.exit()