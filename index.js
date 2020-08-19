import { Client } from 'discord.js';
import dotenv from 'dotenv'

const bot = new Client();
dotenv.config();
const token = process.env.TOKEN;

bot.login(token);

bot.on('ready', () => {
    console.info(`Logged in as ${bot.user.tag}!`)
});

bot.on('message', msg => {
    if (msg.content === '!ping') {
        msg.reply('pong');
        msg.channel.send('pong');
    } else if (msg.content.startsWith('!kick')) {
        if (msg.mentions.users.size) {
            const taggedUser = msg.mentions.users.first();
            msg.channel.send(`You wanted to kick: ${taggedUser.username}`)
        } else {
            msg.reply('Please tag a valid user!')
        }
    }
});

