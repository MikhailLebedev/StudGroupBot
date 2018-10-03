#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <time.h>

volatile pid_t pid;

void handler(int signal)
{
    kill(SIGKILL, 0);
    if (signal == SIGINT){
        raise(SIGKILL);
    }
}

int main(int argc, char **argv)
{
    int status;
    time_t t;
    struct tm *aTm;
    signal(SIGINT, handler);
    signal(SIGQUIT, handler);
    if (argc < 2){
        printf("No args!\n");
    } else {
        printf("Started with arg = %s\n", argv[1]);
    }
    while(1){
        t = time(NULL);
        aTm = localtime(&t);
        printf("%04d/%02d/%02d %02d:%02d:%02d   |   ",aTm->tm_year+1900, aTm->tm_mon+1, aTm->tm_mday, aTm->tm_hour, aTm->tm_min, aTm->tm_sec);
        printf("Starting bot ...\n");
        if(!(pid = fork())){
            printf("---------- Bot log ----------\n");
            execlp("python3", "python3", argv[1], NULL);
            exit(0);
        } else {
            wait(&status);
            printf("-----------------------------\n");
            t = time(NULL);
            aTm = localtime(&t);
            printf("%04d/%02d/%02d %02d:%02d:%02d   |   ",aTm->tm_year+1900, aTm->tm_mon+1, aTm->tm_mday, aTm->tm_hour, aTm->tm_min, aTm->tm_sec);
            printf("Bot fell! Restarting ...\n");
        }
    }
    return 0;
}
