docker cp ig_process_container:/home/ImageWin/util/db/ "$(pwd)"/ImageWin/util/
docker cp ig_process_container:/home/ImageWin/log/ "$(pwd)"/ImageWin/
docker cp ./ ig_process_container:/home/
docker start ig_process_container
docker attach ig_process_container
