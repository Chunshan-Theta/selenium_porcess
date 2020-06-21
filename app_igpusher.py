from ImageWin.util.task.task_db import DbTaskUpdateLoop
from ImageWin.util.task.task_manager import TaskManager
from ImageWin.util.task_crawler import CrawlerTaskNangang, CrawlerTaskSongshan, CrawlerTaskHuashan
from ImageWin.util.task_pic_maker import PicTaskMaker
from ImageWin.util.task_ig import IgTaskPush

manager = TaskManager()
manager.add_task(task_obj=IgTaskPush())
manager.add_task(task_obj=PicTaskMaker())
manager.add_task(task_obj=DbTaskUpdateLoop())
manager.add_task(task_obj=CrawlerTaskNangang())
manager.add_task(task_obj=CrawlerTaskSongshan())
manager.add_task(task_obj=CrawlerTaskHuashan())



manager.loop_run()