import { Client } from 'discord.js';
import dotenv from 'dotenv'

const bot = new Client();
dotenv.config();


bot.on('ready', () => {
    console.info(`Logged in as ${bot.user.tag}!`)
});

bot.on('message', msg => {
    //Probably best to create a command handler of sorts
    switch(msg.content) {
        case "!ping": msg.reply('pong!'); break;
        default:
            if(msg.content.startsWith('!'))
                msg.reply("No valid command provided.... :rage:");
    }
});

bot.login(process.env.TOKEN);
