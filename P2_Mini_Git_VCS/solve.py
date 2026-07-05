# Problem: Mini Git Version Control System

# Background:
# Implement a simplified version of Git.
# There is no filesystem.
# Everything exists only in memory.
# Users interact only through commands.

from __future__ import annotations
from datetime import datetime
import uuid
import math

class File:
    filename : str
    content : str
    last_modified : datetime 
    size : int

    def __init__(self, fn : str, cn : str) -> None:
        self.filename = fn
        self.content = cn
        self.last_modified = datetime.now()
        self.size = math.ceil(len(cn.encode("utf-8")) / 1024)
    
    def new_modification(self) -> None:
        self.last_modified = datetime.now()

    def show_content(self) -> None:
        print("Content: ", self.content)

class Commit:
    commit_id : str
    author : str
    message : str
    timestamp : datetime
    parent_commit : Commit | None = None
    snapshot : list[File]

    def __init__(self, ah : str, ms : str, sn : list[File], pr : Commit | None = None) -> None:
        self.commit_id = uuid.uuid4().hex
        self.author = ah
        self.message = ms
        self.timestamp = datetime.now()
        self.parent_commit = pr
        self.snapshot = sn

class Branch:
    branchName : str
    commits : list[Commit] 
    children : list[Branch]

    def __init__(self, nm : str) -> None:
        self.branchName = nm
        self.commits = []
        self.children = []

    def commit(self, ah : str, ms : str, sn : list[File]) -> None:
        self.commits.append(Commit(ah, ms, sn, self.commits[-1] if len(self.commits) > 0 else None))
        print("commit on branch: ", self.branchName, " successfuly")

    def search(self, bn : str) -> Branch | None:
        if bn == self.branchName:
            return self
        
        for ch in self.children:
            branch : Branch | None = ch.search(bn)
            if branch:
                return branch
            
        return None
    
    def delete(self, bn : str) -> bool:
        for ch in self.children:
            if bn == ch.branchName:
                self.children.remove(ch)
                print("branch and related subbranch deleted successfuly")
                return True
            ch.delete(bn)

        return False
            

class Repository:
    repo_name : str
    tree : Branch

    curr_branch : Branch

    def __init__(self, rn : str) -> None:
        self.repo_name = rn
        self.tree = Branch("main")
        self.curr_branch = self.tree

    def print_curr_branch(self) -> None:
        print(self.curr_branch.branchName)

    def new_branch(self, bn : str) -> None:
        branch : Branch = Branch(bn)
        branch.commits = self.tree.commits
        self.tree.children.append(branch)

    def switch_to_branch(self, bn : str):
        branch : Branch | None = self.tree.search(bn)
        if branch:
            self.curr_branch = branch
            print("switched to branch: ", bn)

    def delete_curr_branch(self) -> None:
        self.tree.delete(self.curr_branch.branchName)
        
class Git:
    user_name : str
    __repo_count : int
    __curr_repo : Repository
    __repos : set[Repository] = set()

    def __init__(self, un : str) -> None:
        self.user_name = un
        self.__repo_count = 0

    def new_repository(self, name : str) -> None:
        repo : Repository = Repository(name)

        self.__curr_repo = repo
        self.__repos.add(repo)
        self.__repo_count += 1

    def get_repo_count(self) -> None:
        print(self.__repo_count)

    def get_curr_repo(self) -> Repository:
        return self.__curr_repo

    def print_curr_repo_name(self) -> None:
        print(self.__curr_repo.repo_name)

    def __set_curr_repo(self, repo : Repository) -> None:
        self.__curr_repo = repo

    def search_repo(self, rn : str) -> Repository | None:
        repo : Repository = Repository("null")
        flag : bool = False
        for r in self.__repos:
            if r.repo_name == rn:
                repo = r
                flag = True
                break
        if flag == True:
            return repo
        return None

    def switch_to_repo(self, rn : str) -> None:
        repo : Repository | None = self.search_repo(rn)
        if repo:
            self.__set_curr_repo(repo)
            print("switched to ", rn)

    def delete(self, rn : str) -> None:
        d_repo : Repository | None = self.search_repo(rn)
        if d_repo:
            self.__repos.remove(d_repo)
            self.__repo_count -= 1
            print("repository deleted successfuly")

def main() -> None:
    git : Git = Git("ansham")

    git.new_repository("project1")
    git.new_repository("project2")
    git.new_repository("project3")

    git.print_curr_repo_name()
    repo : Repository = git.get_curr_repo()

    repo.new_branch("b1")
    repo.new_branch("b2")
    repo.print_curr_branch()
    repo.switch_to_branch("b2")
    repo.print_curr_branch()

    files : list[File] = [File("hello.py", "import numpy"), File("main.py", "run main file")]
    repo.curr_branch.commit("anshm", "this is my first commit", files)
    


    git.delete("project1")

if __name__ == "__main__":
    main()