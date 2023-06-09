/*
 *read file 2 string 
 * $ >input.txt
 * $ g++  file2str.cpp
 * $ ./a.out
*/

#include <iostream>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>

using std::cout; using std::cerr;
using std::endl; using std::string;

string readFileIntoString4(const string& path) {
    struct stat sb{};
    string res;

    int fd = open(path.c_str(), O_RDONLY);
    if (fd < 0) {
        perror("open\n");
    }

    fstat(fd, &sb);
    res.resize(sb.st_size);
    read(fd, (char*)(res.data()), sb.st_size);
    close(fd);

    return res;
}

/*
int main(int argc, char * argv[])
{
    string filename("input.txt");
    string file_contents;

  	if (argc != 3) {
		cout << argv[0] << " pattern.json " << "file" << endl;
		return 0;
	}
		
	cout << "file 1" << endl; 
    file_contents = readFileIntoString4(argv[1]);
    cout << file_contents << endl;
	cout << "file 2" << endl;
    file_contents = readFileIntoString4(argv[2]);
    cout << file_contents << endl;

    exit(EXIT_SUCCESS);
}
*/
