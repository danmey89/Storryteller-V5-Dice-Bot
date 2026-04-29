import os
from typing import List 

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

def roll_v5(r_dice: int, h_dice=0) -> tuple[int, List, List, str]:
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

    if success_sum== 0 and botch != 0:
        special = "botch"
    elif success_sum == 0:
        special = "zero"
    elif len(crit_type) > 1:
        success_sum += (len(crit_type) // 2)
        if crit_hun > 1 or (crit_hun == 1 and (crit_reg % 2) != 0):
            special = "messy"
        else:
            special = "critical"

    return success_sum, results_reg, results_hun, special 


# d10 roller with optional success level counter, optional exploding dice

def roll_10_success_count(n_dice: int, threshold=99, count_success=False, x_again="n") -> tuple[List, int|None]:
    results = []
    p = 0
    success = 0

    def append_result(p: int):
        
        # adds extra die roll for any 10 rolled, 1 on extra die is disregarded

        r = random.randint(1, 10)
        if p == 10 and r == 1:
            return

        results.append(r)
        p = r
        if r != 10:
            return

        append_result(p)
    
    # with success counter

    if count_success:

        match x_again.lower(): 
            case "n":
                for _ in range(n_dice):
                    results.append(random.randint(1, 10))
            case "x":                           # exploding dice
                for _ in range(n_dice):
                    append_result(p)
            case "d":                           # double result on 10
                for _ in range(n_dice):
                    r = random.randint(1, 10)
                    results.append(r)
                    if r == 10:
                        success += 1

        for i in results:
            if i >= threshold:
                success += 1
            elif i == 1:
                success -=1

        return results, success
        
    # simple dice roller

    if x_again.lower() == "n":

       for _ in range(n_dice):
            results.append(random.randint(1, 10))

       return results, None
    
    # exploding dice

    for _ in range(n_dice):
            append_result(p)

    return results, None


# dice-roller for cod

def roll_cod(n_dice: int, x_again=10) ->  tuple[List, int]:
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
                answer = f"Results for **{ctx.author.global_name}**: \n{results[1]}, {results[2]} \n**Bestial Failure**" 
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
            results = roll_10_success_count(int(args[0]))
        elif len(args) == 2:
            if args[1].isnumeric():
                count_success = True
                results = roll_10_success_count(int(args[0]), threshold=int(args[1]), count_success=count_success)
            else:
                results = roll_10_success_count(int(args[0]), x_again=args[1])
        elif len(args) == 3:
            count_success = True
            if not args[1].isnumeric() or args[2].isnumeric():
                raise ValueError
            results = roll_10_success_count(int(args[0]), threshold=int(args[1]), x_again=args[2], count_success=count_success)
        else:
            raise ValueError


        if count_success:
             await ctx.send(f"Results for **{ctx.author.global_name}**: \n{results[0]} \n**{results[1]}** successes")
        else:
            await ctx.send(f"Results for **{ctx.author.global_name}**: \n{results[0]}")

    except ValueError:
        await ctx.send('incorrect or insufficient arguments \n- please enter the total amount of dice \n- optionally add a target value for successes \n- add an "x" for exploding dice pools or \n- add a "d" for double success on 10')


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



