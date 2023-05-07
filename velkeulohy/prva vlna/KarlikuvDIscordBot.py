from os import getenv
import requests, random
from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from notifiers import get_notifier
import asyncio
load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")
IMGFLIP_API_URL = "https://api.imgflip.com"
UNAME=getenv("NAME")
PWORD=getenv("PASSWORD")
LOGIN=getenv("EMAIL_LOGIN")
PASS=getenv("EMAIL_PASS")
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix="!", case_insensitive=True, intents=intents
)


class MemeGenerator:
    def __init__(self) -> None:
        # Sem mĂ´Ĺľete pridaĹĄ vlastnĂ© atribĂşty.
        pass

    def list_memes(self) -> str:
        # TODO: Implementujte tĂşto metĂłdu
        # Tip 1: PreÄŤĂ­tajte si dokumentĂˇciu imgflip API.
        # Tip 2: Pomocou modulu requests vytvorte GET poĹľiadavku na
        #        endpoint https://api.imgflip.com/get_memes.
        # Tip 3: PreskĂşmajte, ako vyzerĂˇ odpoveÄŹ API (response.json()).
        resp=requests.get(f'{IMGFLIP_API_URL}/get_memes')
        some_list=[]
        for i in resp.json()['data']['memes']:
            some_list.append((i['id'], i['name']))
            if len(some_list)==25:
                break
        return some_list

    def make_meme(
        self, template_id: int, top_text: str, bottom_text: str
    ) -> str:
        # TODO: Implementujte tĂşto metĂłdu
        # Tip 1: Pomocou modulu requests vytvorte POST poĹľiadavku na
        #        endpoint https://api.imgflip.com/caption_image.
        # Tip 2: PouĹľite parameter `params` na vloĹľenie parametrov.
        # Tip 3: PreskĂşmajte, ako vyzerĂˇ odpoveÄŹ API (response.json()).

        # VrĂˇĹĄte URL vygenerovanĂ©ho meme.
        resp=requests.post(f'{IMGFLIP_API_URL}/caption_image?template_id={template_id}&username={UNAME}&password={PWORD}&text0={top_text}&text1={bottom_text}')
        my_data= resp.json()['data']['url']
        return my_data

class MentionsNotifier:
    def __init__(self, sub_dict) -> None:
        self.sub_dict=sub_dict
        # Sem mĂ´Ĺľete pridaĹĄ vlastnĂ© atribĂşty.
    def subscribe(self, user_id: int, email: str) -> None:
        # TODO: Implementujte tĂşto metĂłdu.
        self.sub_dict[user_id]=email
        print(self.sub_dict)
        return self.sub_dict
    def unsubscribe(self, user_id: int) -> None:
     # TODO: Implementujte tĂşto metĂłdu
        for key in self.sub_dict:
            if key == user_id:
                del self.sub_dict[key]
        print(self.sub_dict)
        return self.sub_dict

    def notify_about_mention(self, user_id: int, msg_content: str, url) -> None:
        # TODO: Implementujte tĂşto metĂłdu.
        email = get_notifier('email')
        settings = {
                'host': 'ksi2022smtp.iamroot.eu',
                'port': 587,
                'tls': True,

                'username': LOGIN,
                'password': PASS,

                'to':self.sub_dict[user_id],
                'from': 'user3763@ksi2022smtp.iamroot.eu',

                'subject':"Some subject",
                'message': f"Someone mentioned you in channel {url}, {msg_content}",
            }
        email.notify(**settings)
class Hangman:
    # TODO: VyuĹľite tĂşto triedu pri implementĂˇcii hry hangman,
    #       vytvorenie atribĂştov a metĂłd je na vĂˇs.
    def __init__(self) -> None:
        self.game='**Hangman**'
        self.message=None
        self.player=None
        self.game_start=None


    def play_hg(self):
        #if self.lives or status == won start again
        #clear lives, status, guesses
        with open('words.txt', 'r') as file:
            lines = file.readlines()
            word=random.choice(lines)
        self.word=word
        cipher = ''
        for i in self.word:
            cipher+='-'
        self.cipher=cipher[:-1]
        self.guesses=[]
        self.lives=7
        self.status=''
        ret_statement=f'**{self.game}**\nPlayer:{self.player}\nGuesses:{self.guesses}\nLives:{self.lives}\nWord:{self.cipher}\n{self.status}'
        return ret_statement
    def guess_hg(self,letter):
        if letter not in self.guesses:
            self.guesses.append(letter)
        if letter in self.guesses:
            self.status='You already guessed that.'
        indexes=[]
        if letter in self.word:
            self.status='Correct guess.'
            indexes=[i for i, ltr in enumerate(self.word) if ltr == letter]
            for j in indexes:
                self.cipher=self.cipher[:j]+letter+self.cipher[j+1:]
            if '-' not in self.cipher:
                self.status='You won!'
        
        if letter not in self.word:
            self.status='Incorrect guess.'
            self.lives-=1
            if letter not in self.guesses:
                self.status='You already guessed that.'
            if self.lives<1:
                self.status=f'You lost! The word was {self.word}'

# --------- LEVEL 1 ----------
meme_generator = MemeGenerator()


@bot.command(name="list_memes")
async def list_memes(ctx: Context) -> None:
    meme_list = meme_generator.list_memes()
    # TODO: PoslaĹĄ meme_list do kanĂˇla.
    for j in meme_list:
        j=str(j)
        j=j.translate(str.maketrans({"(":"", ")":"", "'":"", ",":"", '"':'', '"':''}))
        await ctx.send(f'{j}\n')


@bot.command(name="make_meme")
async def make_meme(
    ctx: Context, template_id: int, top_text: str, bottom_text: str
) -> None:
    meme_url = meme_generator.make_meme(template_id, top_text, bottom_text)
    # TODO: PoslaĹĄ meme_url do kanĂˇla.
    await ctx.send(meme_url)    

# --------- LEVEL 2 ----------
some_dict={}
mentions_notifier = MentionsNotifier(some_dict)


@bot.command(name="subscribe")
async def subscribe(ctx: Context, email: str) -> None:
    mentions_notifier.subscribe(ctx.author.id, email)
    await ctx.send('email zaregistrovany')


@bot.command(name="unsubscribe")
async def unsubscribe(ctx: Context) -> None:
    mentions_notifier.unsubscribe(ctx.author.id)
    await ctx.send('email odregistrovany')


@bot.event
async def on_message(message: Message) -> None:
    # TODO: upravte tĂşto funkciu tak, aby v prĂ­pade oznaÄŤenia pouĹľĂ­vateÄľa
    #       v sprĂˇve `message` mu bolo poslanĂ© oznĂˇmenie.
    mentions=message.raw_mentions
    for id in mentions:
        mentions_notifier.notify_about_mention(id, message.content, message.jump_url)

    # NasledujĂşci riadok nemodifikujte, inak prĂ­kazy bota nebudĂş fungovaĹĄ.
    await bot.process_commands(message)

# --------- LEVEL 3 ----------
hangman = Hangman()


@bot.command(name="play_hangman")
async def play_hangman(ctx: Context) -> None:
    # TODO: Implementujte tento prĂ­kaz s vyuĹľitĂ­m triedy Hangman.
    hangman.player=ctx.author
    #hangman.message=ctx.message.id
    game_info=hangman.play_hg()
    game_start=await ctx.send(game_info)
    hangman.game_start=game_start

@bot.command(name="guess")
async def guess(ctx: Context, letter: str) -> None:
    # TODO: Implementujte tento prĂ­kaz s vyuĹľitĂ­m triedy Hangman
    # load game where player is msg author !!!!!!!!!!!
    char=hangman.guess_hg(letter)
    guess_msg=ctx.message
    msg=hangman.game_start
    new_msg=f'**{hangman.game}**\nPlayer:{hangman.player}\nGuesses:{hangman.guesses}\nLives:{hangman.lives}\nWord:{hangman.cipher}\n{hangman.status}'
    await Message.edit(msg, content=new_msg)
    await asyncio.sleep(3)
    await Message.delete(guess_msg)
bot.run(TOKEN)