#include <cstdlib>
#include <iostream>
#include <fstream>
#include <stack>
#include <list>
#include <iterator>
#include <vector>

using namespace std;

    typedef vector<list<int> > grafo;
    typedef vector<int> vet;
    ofstream saida("ciclos.txt");



void bt(int v, int &f, int s,grafo &G, vet &mark, vet &ps, vet &ms) {
     int g;
     list<int>::iterator i;
     vector<int>::iterator j;
     f = 0;
     ps.push_back(v);
     mark[v]=1;
     ms.push_back(v);
     for(i=G[v].begin(); i != G[v].end(); ++i) {
                         
        if (*i<s) {
//            G[v].erase(i);
        }
        else if (*i==s) {
             for(j=ps.begin(); j != ps.end(); ++j) {
                saida << *j << " ";
             }
             saida << endl;
             f=1;
        }
        else if (!mark[*i]) {
             bt(*i,g,s,G,mark,ps,ms);
             f = f || g;
        }
     }   
     if (f) {
        while (ms.back()!=v) {
              mark[ms.back()]=0;
              ms.pop_back();
        }
        cout << endl;
        ms.pop_back();
        mark[v]=0;
     }
//     system("PAUSE");
     ps.pop_back();
}




int main(int argc, char *argv[])
{
    int n,a,c;
    list<int>::iterator t;
     
    ifstream entrada("grafo.txt");     
    entrada >> n;
    grafo F(n);
    for (int i=0;i<n;i++) {
        entrada >> c;
        entrada >> c;
        for (int j=0;j<c;j++) {
            entrada >> a;
            F[i].push_front(a);
        }
    }
    entrada.close();

    vector <int> mark(n,0);
    int s,flag;
    vector <int> ps;
    vector <int> ms;

    for(s=0;s<n;s++) {
         bt(s,flag,s,F,mark,ps,ms);
         while (!ms.empty()) {
               mark[ms.back()]=0;
               ms.pop_back();
         }
    }

    saida.close();
}

