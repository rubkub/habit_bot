import json
import telebot
import datetime
from datetime import timedelta


my_token = 'Ваш токен'
bot = telebot.TeleBot(token=my_token)
HABITS_FILE = 'Ваш файл .json'


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для записи твоих привычек. Используй /add_habit для добавления привычки, /mark_habit для отметки привычки, /list_habits для просмотра привычек, /delete_habit для удаления привычки, /edit_habit для изменения привычки, /delete_habit для удаления привычки, /stats для показа статистики выполнения привычек и /reminders для уведомления о сегодняшних привычках.')

@bot.message_handler(commands=['add_habit'])
def add_habit(message):
    bot.send_message(message.chat.id, 'Введите привычку, которую вы хотите добавить:')
    bot.register_next_step_handler(message, process_habit_input)

def process_habit_input(message):
    habit_text = message.text.strip()
    bot.send_message(message.chat.id, 'Введите частоту привычки:')
    bot.register_next_step_handler(message, process_habit_frequancy, habit_text)

def process_habit_frequancy(message, text):
    habits = open_habits()

    freq = int(message.text.strip())
    date = datetime.datetime.now().strftime('%Y-%m-%d')

    habit = {'name': text, 'userId': message.from_user.id, 'frequency': freq, 'createDate': date, 'progress': []}
    habits.append(habit)
  
    with open(HABITS_FILE, 'w') as write_file:
      json.dump(habits, write_file)

    bot.send_message(message.chat.id, 'Привычка добавлена.')

@bot.message_handler(commands=['mark_habit'])
def mark_habit(message):
    bot.send_message(message.chat.id, 'Введите название привычки:')
    bot.register_next_step_handler(message, process_mark_habit)

def process_mark_habit(message):
    habits = open_habits()
    
    habit_text = message.text.strip()
    date = datetime.datetime.now().strftime('%Y-%m-%d')

    for habit in habits:
       if habit['name'] == habit_text:
          habit['progress'].append(date)

    with open(HABITS_FILE, "w") as write_file:
      json.dump(habits, write_file)

    bot.send_message(message.chat.id, 'Прогресс сохранён.')

@bot.message_handler(commands=['list_habits'])
def list_habits(message):
  user_id = message.from_user.id

  habits = open_habits()

  if habits:
    habits_list = '\n'.join([f'- {habit["name"]}' for habit in habits])
    bot.send_message(message.chat.id, f'Ваши привычки:\n{habits_list}')
  else:
    bot.send_message(message.chat.id, 'Вы пока не добавили привычек.')

@bot.message_handler(commands=['delete_habit'])
def delete_habits(message):
  bot.send_message(message.chat.id, ('Введите наименование привычки, которую вы хотите удалить:'))
  bot.register_next_step_handler(message, process_habit_delete)

def process_habit_delete(message):
  habit_text = message.text.strip()
  habits = open_habits()

  for habit in habits:
    if habit['name'] == habit_text:
      habits.remove(habit)
  with open(HABITS_FILE, 'w') as write_file:
      json.dump(habits, write_file)

  bot.send_message(message.chat.id, 'Привычка удалена.')

@bot.message_handler(commands=['edit_habit'])
def edit_habits(message):
  bot.send_message(message.chat.id, ('Введите наименование привычки, которую вы хотите изменить:'))
  bot.register_next_step_handler(message, process_habit_edit_one)

def process_habit_edit_one(message):
    habit_text = message.text.strip()
    bot.send_message(message.chat.id, 'Введите новое наименование:')
    bot.register_next_step_handler(message, process_habit_edit_two, habit_text)  

def process_habit_edit_two(message, old_habit_text):
    new_habit_text = message.text.strip()
    bot.send_message(message.chat.id, 'Введите новую частоту:')
    bot.register_next_step_handler(message, process_habit_edit, old_habit_text, new_habit_text)  

def process_habit_edit(message, old_habit_text, new_habit_text):
    habits = open_habits()

    freq = int(message.text.strip())

    for habit in habits:
       if habit['name'] == old_habit_text:
          habit['name'] = new_habit_text
          habit['frequency'] = freq
  
    with open(HABITS_FILE, 'w') as write_file:
      json.dump(habits, write_file)
    
    bot.send_message(message.chat.id, 'Привычка обновлена.')

@bot.message_handler(commands=['stats'])
def stats(message):
  user_id = message.from_user.id
  
  habits = open_habits()

  if habits:
    habits_list = '\n'.join([f'- {habit["name"]}: {habit["progress"]}' for habit in habits])
    bot.send_message(message.chat.id, f'Ваши привычки:\n{habits_list}')
  else:
    bot.send_message(message.chat.id, 'Вы пока не добавили привычек.')

@bot.message_handler(commands=['reminders'])
def remind(message):
  habits = open_habits()
  habits_list = []

  date = datetime.date.today()
  for habit in habits:
      if not habit['progress']: 
        createDate = datetime.datetime.strptime(habit['createDate'], '%Y-%m-%d').date()
        if timedelta(days=habit['frequency']) + createDate <= date:
           habits_list.append(habit["name"])
      else: 
        lastDate = datetime.datetime.strptime(habit['progress'][-1], '%Y-%m-%d').date()
        if timedelta(days=habit['frequency']) + lastDate <= date:
           habits_list.append(habit["name"])
  
  bot.send_message(message.chat.id, 'Напоминание на сегодня:\n- ' + '\n- '.join(habits_list))

def open_habits():
  habits = []
  try:
      with open(HABITS_FILE, 'r', encoding='utf-8') as f:
        habits = json.load(f)
  except FileNotFoundError:
      habits = []
  return habits


bot.polling(none_stop=True)