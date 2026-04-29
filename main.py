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

def roll_v5(r_dice: int, h_dice=0):
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

    for _ in range(r_dice-h_dice):
        r = random.randint(1, 10)
        results_reg.append(r)
        if r >= threshold:
            success_sum += 1
            if r == 10:
                crit_reg += 1
                crit_type.append("r")

    # rolling special dice and record results

    for _ in range(h_dice):
        r = random.randint(1, 10)
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


# simple d10 dice roller

def roll_10(n_dice: int, x_again="n"):
    results = []
    p= 0

    if x_again.lower() != "x":

       for _ in range(n_dice):
            results.append(random.randint(1, 10))

       return results

    def append_result(p: int):
        
        # adds extra die roll for any 10 rolled a 1 on an extra die is disregarded

        r = random.randint(1, 10)
        if p == 10 and r == 1:
            return

        results.append(r)
        p = r
        if r != 10:
            return

        append_result(p)

    for _ in range(n_dice):
        append_result(p)

    return results


# d10 roller with success level counter

def roll_10_success_count(n_dice: int, threshold: int, x_again="n"):
    results = []
    p = 0
    success = 0
    
    if x_again.lower() != "x":

       for _ in range(n_dice):
            results.append(random.randint(1, 10))
    
       for i in results:
            if i >= threshold:
                success += 1
            elif i == 1:
                success -=1

       return results, success


    def append_result(p: int):
        
        # adds extra die roll for any 10 rolled a 1 on an extra die is disregarded

        r = random.randint(1, 10)
        if p == 10 and r == 1:
            return

        results.append(r)
        p = r
        if r != 10:
            return

        append_result(p)

    for _ in range(n_dice):
        append_result(p)

    for i in results:
        if i >= threshold:
            success += 1
        elif i == 1:
            success -=1


    return results, success


# dice-roller for cod

def roll_cod(n_dice: int, x_again=10):
    results = []
    success = 0
    threshold = 8

    def append_result():
        r = random.randint(1, 10)
        results.append(r)
        if r < x_again:
            return

        append_result()

    for i in range(n_dice):
        append_result()

    for i in results:
        if i >= threshold:
            success += 1

    return results, success


# command VtM roller

@bot.command(name="vroll")
async def roll_bones(ctx: discord.AppCommandContext, *args):

    try:
        if len(args) == 2:
            results = roll_v5(int(args[0]), int(args[1]))
        elif len(args) == 1:
            results = roll_v5(int(args[0]))
        else:
            raise ValueError

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

    except ValueError:
        await ctx.send('insufficient arguments \n- please enter the total amount of dice \n- optionally add the hunger level')
        

# rouse check command

@bot.command(name="rouse")
async def rouse_check(ctx: discord.AppCommandContext):
    check = random.randint(1, 10)

    if check >= 6:
        await ctx.send(f"result for **{ctx.author.global_name}**: {check} \n**Success!**")
    else:
        await ctx.send(f"result for **{ctx.author.global_name}**: {check} \n**Failed!**")


# command d10 roller

@bot.command(name="r")
async def roll10(ctx: discord.AppCommandContext, *args):
    count_success = False
    
    try:

        if len(args) == 1:
            results = roll_10(int(args[0]))
        elif len(args) == 2:
            if args[1].isnumeric():
                results = roll_10_success_count(int(args[0]), int(args[1]))
                count_success = True
            else:
                results = roll_10(int(args[0]), args[1])
        elif len(args) == 3:
            if not args[1].isnumeric():
                raise ValueError
            if args[2].isnumeric():
                raise ValueError
            results = roll_10_success_count(int(args[0]), int(args[1]), args[2])
            count_success = True
        else:
            raise ValueError

        if count_success:
             await ctx.send(f"Results for **{ctx.author.global_name}**: {results[0]}\n **{results[1]}** successes\n")
        else:
            await ctx.send(f"Results for **{ctx.author.global_name}**: {results}")

    except ValueError:
        await ctx.send('incorrect or insufficient arguments \n- please enter the total amount of dice \n- optionally add a target value for successes \n- add an "x" for exploding dice pools')


# command CoD roller

@bot.command(name="croll")
async def roll_chrones(ctx: discord.AppCommandContext, *args):

    try:
        if len(args) == 1:
            results = roll_cod(int(args[0]))
        elif len(args) == 2:
            results = roll_cod(int(args[0]), int(args[1]))
        else:
            raise ValueError

        await ctx.send(f"Results for **{ctx.author.global_name}**: {results[0]}\n **{results[1]}** successes\n")

    except ValueError:
        await ctx.send('incorrect or insufficient arguments \n- please enter the total amount of dice \n- optionally add a value for x-again (standart 10)')

bot.run(TOKEN)



