import os 

from discord.ext import commands
import discord
from dotenv import load_dotenv
import random



load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(intents=intents, command_prefix="!")

# dice-roller vor VtM 5th ed.

def roll_v5(r_dice, h_dice):
    dtype = 10
    results_reg = []
    results_hun = []
    threshold = 6
    success_sum = 0
    crit_reg = 0
    crit_hun = 0
    crit_type = []
    botch = 0
    special = "" 
    
    # rolling regular dice and record results

    for _ in range(int(r_dice)-int(h_dice)):
        r = random.randint(1, dtype)
        results_reg.append(r)
        if r >= threshold:
            success_sum += 1
            if r == 10:
                crit_reg += 1
                crit_type.append("r")

    # rolling special dice and record results

    for _ in range(int(h_dice)):
        r = random.randint(1, dtype)
        results_hun.append(r)
        if r >= threshold:
            success_sum += 1
            if r == 10:
                crit_hun += 1
                crit_type.append("h")
        if r == 1:
            botch += 1


    # test for special conditions (criticals, messy criticals, botches)
    if success_sum == 0:
        special = "zero"
    elif success_sum== 0 and botch != 0:
        special = "botch"
    elif len(crit_type) > 1:
        success_sum += (len(crit_type) // 2) * 2
        if len(crit_type) % 2 == 0:
            for crit in crit_type:
                if crit == "h":
                    special = "messy"
                else:
                    special = "critical"
        else:
            for crit in crit_type[1:]:
                if crit == "h":
                    special = "messy"
                else:
                    special = "critical"
      

    return success_sum, results_reg, results_hun, special 


# dice-roller for cod

def roll_cod(n_dice):
    dtype = 10
    count = int(n_dice) 
    results = []
    success = 0
    threshould = 8

    x_again = 10
    
    def append_result():
        r = random.randint(1, dtype)
        results.append(r)
        if r < x_again:
            return

        append_result()

    for i in range(count):
        append_result()

    for i in results:
        if i >= threshould:
            success += 1

    return results, success

# command to engage VtM roller

@bot.command(name="vroll")
async def roll_bones(ctx: discord.AppCommandContext, regular_dice: int, hunger_dice: int):
    results = roll_v5(regular_dice, hunger_dice)

    match results[3]:
        case "critical":
            answer= f"Results for **{ctx.author.global_name}**: \n{results[1]}, {results[2]} \n**{results[0]}** Successes \n**Critical Success**" 
        case "messy":
            answer= f"Results for **{ctx.author.global_name}**: \n{results[1]}, {results[2]} \n**{results[0]}** Successes \n**Messy Critical**" 
        case "botch":
            answer = f"Results for **{ctx.author.global_name}**: \n{results[1]}, {results[2]} \n**Botch**" 
        case "zero":
            answer = f"Results for **{ctx.author.global_name}**: \n{results[1]}, {results[2]} \n**No Success**" 
        case _:
            answer= f"Results for **{ctx.author.global_name}**: \n{results[1]}, {results[2]} \n**{results[0]}** Successes" 

    await ctx.send(answer)

# error-handling for insufficient number of arguments

@roll_bones.error
async def v_input_error(ctx: discord.AppCommandContext, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('insufficient arguments \nplease enter the total amount of dice and the number of hunger-dice')


# rouse check command

@bot.command(name="rouse")
async def rouse_check(ctx: discord.AppCommandContext):
    check = random.randint(1, 10)

    if check >= 6:
        await ctx.send(f"result for **{ctx.author.global_name}**: {check} \n**Success!**")
    else:
        await ctx.send(f"result for **{ctx.author.global_name}**: {check} \n**Failed!**")


# command to engage CoD roller

@bot.command(name="croll")
async def roll_chrones(ctx: discord.AppCommandContext, dice: int):
    results = roll_cod(dice)

    answer = f"Results for **{ctx.author.global_name}**: {results[0]}\n **{results[1]}** successes\n"

    await ctx.send(answer)


bot.run(TOKEN)



