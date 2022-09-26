mkdir -p Bin

g++ -g -rdynamic -Wpedantic -std=c++17 -o ./Bin/frame_unpacker frame_unpacker.cpp

g++ -g -rdynamic -Wpedantic -O4 -std=c++17 -o ./Bin/frame_unpacker_bis frame_unpacker_bis.cpp

g++ -g -rdynamic -Wpedantic -O4 -std=c++17 -o ./Bin/frame_unpacker_tris frame_unpacker_tris.cpp -lpthread
