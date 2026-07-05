# Problem: Log Analytics Engine (Difficulty: 7.5/10)
# This simulates a backend service that receives server logs and allows users to query them using commands.

# Input Format
# Each log entry is a single string:
# LOG|timestamp|server|level|module|message

# Commands
# SHOW ALL
# SHOW ERRORS
# SHOW SERVER ServerA
# SHOW MODULE AUTH
# SHOW LEVEL INFO
# COUNT ERRORS
# COUNT SERVER ServerA
# COUNT LEVEL WARNING
# LATEST
# OLDEST
# SORT TIME
# SORT LEVEL
# EXIT

# -----------------------------------------------------------------------------------------------------------------------------------

input_data = """
            LOG|2026-06-28 10:30:12|ServerA|INFO|AUTH|User logged in
            LOG|2026-06-28 10:31:15|ServerB|ERROR|DATABASE|Connection timeout
        """

class Solution:
    logs : list[list[str]] = []
    output : str = ""

    def __parse_input(self) -> None:
        lines : list[str] = (input_data.strip()).split("\n")
        for l in lines:
            self.logs.append((l.strip()).split("|"))

    def __show_all(self) -> None:
        for i in self.logs:
            print(f"{i[2]}\n{i[3]}\n{i[4]}\n{i[5]}\n")

    def __show_errors(self) -> None:
        for i in self.logs:
            if i[3].upper() == "ERROR":
                print(f"{i[2]}\n{i[3]}\n{i[4]}\n{i[5]}\n")

    def __show_server(self, sname : str) -> None:
        for i in self.logs:
            if i[2].upper() == sname:
                print(f"{i[2]}\n{i[3]}\n{i[4]}\n{i[5]}\n") 

    def __show_module(self, mname : str) -> None:
        for i in self.logs:
            if i[4].upper() == mname:
                print(f"{i[2]}\n{i[3]}\n{i[4]}\n{i[5]}\n") 

    def __show_level(self, lname : str) -> None:
        for i in self.logs:
            if i[3].upper() == lname.upper():
                print(f"{i[2]}\n{i[3]}\n{i[4]}\n{i[5]}\n")

    def __count_errors(self) -> None:
        count = 0
        for i in self.logs:
            if i[3].upper() == "ERROR":
                count += 1
        
        print(count)

    def __count_level(self, lname : str) -> None:
        count = 0
        for i in self.logs:
            if i[3].upper() == lname.upper():
                count += 1
        
        print(count)

    def __count_server(self, sname : str) -> None:
        count = 0
        for i in self.logs:
            if i[2].upper() == sname.upper():
                count += 1
        
        print(count)

    
    def __operation(self, opr : str) -> None:
        op = opr.strip().split(" ")

        if len(op) == 1:
            if opr == "LATEST":
                i = self.logs[0]
                print(f"{i[2]}\n{i[3]}\n{i[4]}\n{i[5]}\n")
            elif opr == "OLDEST":
                i = self.logs[-1]
                print(f"{i[2]}\n{i[3]}\n{i[4]}\n{i[5]}\n")
            else:
                print("Invalid Operation")
        elif len(op) == 2:
            if opr == "SHOW ALL":
                self.__show_all()
            elif opr == "SHOW ERROR":
                self.__show_errors()
            elif opr == "COUNT ERROR":
                self.__count_errors()
            else:
                print("Invalid Operation")
        elif len(op) == 3 and op[0] == "SHOW":
            if op[1] == "SERVER":
                self.__show_server(op[2].strip())
            elif op[1] == "MODULE":
                self.__show_module(op[2].strip())
            elif op[1] == "LEVEL":
                self.__show_level(op[2].strip())
            else:
                print("Invalid Operation")   
        elif len(op) == 3 and op[0] == "COUNT":
            if op[1] == "SERVER":
                self.__count_server(op[2].strip())
            elif op[1] == "LEVEL":
                self.__count_level(op[2].strip())
            else:
                print("Invalid Operation")
        else:
            print("Invalid Operation")

    
    def solve(self) -> None:
        self.__parse_input()

        self.logs.sort(key=lambda x : x[1])

        while True:
            op : str = str(input()).upper()
            if(op == "EXIT"):
                break
            self.__operation(op)


        
sol = Solution()
sol.solve()