import discord
import GameDeal as gd

from discord.ext import commands, tasks
from tokens import DISCORD_TOKEN

REDIRECT_URI = 'http://localhost:5000/callback'

#call commands by typing command prefix before the command
COMMAND_PREFIX = "your-command-prefix-here"

GAMES_FILE_PATH = "games.txt"

NOTIFICATION_CHANNEL_ID = "your-channel-id-here"

def run_discord_bot():
    bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=discord.Intents.all())
    global trackedGames, dealToLastMessageId, lastMessageIdToDeal
    dealToLastMessageId = {}
    lastMessageIdToDeal = {}
    trackedGames = []

    # execute on bot startup
    @bot.event
    async def on_ready():
        global trackedGames
        with open(GAMES_FILE_PATH, "r") as file:
            trackedGames = [gd.GameDeal(title = line.strip()) for line in file.readlines()]
            print(f"number of tracked deals: {len(trackedGames)}")
        print(f'{bot.user} is now running')
        check_prices.start()


    # execute on message sent
    @bot.event
    async def on_message(message):
        # check if message was sent by the bot
        if message.author == bot.user:
            return
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: \"{user_message}\" in \"{channel}\"')

        await bot.process_commands(message)

    
    # track game prices from isthereanydeal api
    @bot.command()
    async def track(ctx, *args):
        if args[0] == "game":
            await track_game(ctx," ".join(args[1:]))

    @bot.command()
    async def track_game(ctx, *args):
        global trackedGames
        game = gd.GameDeal(title = " ".join(args))
        if game.isValid():
            if game not in trackedGames:
                with open(GAMES_FILE_PATH, "a") as file:
                    file.write(game.get_title() + "\n")
                    file.close()
                trackedGames.append(game)
            deals = game.get_best_deals()
            await send_deals(channelId = ctx.channel.id, game = game, deals = deals)
        else:
            await ctx.send("Game not found; try checking the spelling or copying the game title from steam")
    

    async def send_deals(channelId, game, deals):
        channel = bot.get_channel(channelId)
        embed = discord.Embed(title = f"Top {len(deals)} {game.get_title()} Deals")
        for deal in deals:
            if deal['voucher']:
                embedName = f"Store: {deal['store']}, Price: ${deal['price']:.2f}, Voucher: {deal['voucher']}"
            else:
                embedName = f"Store: {deal['store']}, Price: ${deal['price']:.2f}"
            embed.add_field(name = embedName,
                            value = f"[Store Page]({deal['url']})",
                            inline = False) 
            embed.add_field(name = " ", value = "", inline = False) # new line
        
        embed.add_field(name = "React to most recent deals to stop tracking this game",
                        value = "",
                        inline = False)
        
        message = await channel.send(embed=embed)
        addToDicts(dealToLastMessageId, lastMessageIdToDeal, key = game.get_title(), value = message.id)


    def addToDicts(dict1, dict2, key, value):
        if key in dict1:
            dict2.pop(dict1[key])
        elif value in dict2:
            dict1.pop(dict2[value])
        dict1[key] = value
        dict2[value] = key


    @tasks.loop(hours = 12)
    async def check_prices():
        global trackedGames
        for game in trackedGames:
            game.refresh_deals()
            deals = game.get_best_deals()
            await send_deals(channelId = NOTIFICATION_CHANNEL_ID, game = game, deals = deals)
            
    
    @bot.event
    async def on_reaction_add(reaction, user):
        global lastMessageIdToDeal
        if user == bot.user:
            return
        if reaction.message.id in lastMessageIdToDeal:
            gameTitle = lastMessageIdToDeal[reaction.message.id]
            trackedGames.remove(gd.GameDeal(gameTitle))
            lastMessageIdToDeal.pop(reaction.message.id)
            dealToLastMessageId.pop(gameTitle)
            with open(GAMES_FILE_PATH, "w") as file:
                for game in trackedGames:
                    file.write(game.get_title() + "\n")
                file.close()
                


    bot.run(DISCORD_TOKEN)
