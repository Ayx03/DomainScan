#include <iostream>
#include <fstream>
#include <iomanip>

using namespace std;

int main() {
    ofstream outfile("6numbers"); // 创建输出文件流
    if (!outfile) { // 如果文件打开失败
        cerr << "Cannot open file." << endl;
        return 1;
    }

    for (int i = 0; i < 1000000; i++) { // 生成 000000 - 999999 的序号
        outfile << setw(6) << setfill('0') << i << endl; // 将序号写入文件
    }

    outfile.close(); // 关闭文件流
    return 0;
}
