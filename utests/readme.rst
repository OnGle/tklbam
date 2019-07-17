Testing
=======
    
New tklbam testing for python3, now uses the builtin unittest module, below is a list of all the new tests.
Which of the old regression tests they correlate with along with additional information that may be useful
for debugging. If you just want to run the tests then do as follows.

``cd utests``
``python3 -m unittest discover`` OR ``./runTests.sh``

.. note::

    running "./runTests.sh" with the ``-v`` switch will add rudimentary colorization ontop of the verbose
    output provided by unittest


Details
-------

 - TestDirIndex.test_creation
    ensures dirindex.create creates a dirindex, does NOT test it's correctness

    correlates with (but does not fully replace) "1 - dirindex creation"

 - TestDirIndex.test_creation_correct
    ensures dirindex.create creates a dirindex with an internally correct
    representation of the directory tree provided.
        - ensures all files/dirs in tree are found
        - ensures all mode, uid, gid, size and mtime of all files/dirs
            are correct

    correlates with "1 - dirindex creation"

 - TestDirIndex.test_fromfile_correct
    exactly the same as "TestDirIndex.test_fromfile_correct" but performs
    tests "AFTER" reloading the DirIndex from file.

 - TestDirIndex.test_creation_with_limitation_correct
    ensures dirindex.create creates a dirindex with an internally correct
    representation of the directory tree provided when limitations are
    specified.
        - ensures all files/dirs in tree are found
        - ensures all mode, uid, gid, size and mtime of all files/dirs
            are correct
        - ensures no extra files which should have been skipped are
            collected.

    correlates with "2 - dirindex creation with limitation"

 - TestDirIndex.test_dirindex_delta
    ensures changes.whatchanged can correctly identify changes of uid, gid,
    mode, file contents, symlink location as well as new files and deleted
    or moved files between dirindicies.

    roughly correlates with "3 - dirindex comparison"

- TestDirIndex.test_fixstat
    tests rolling back stat changes (that is uid, gid and mode) correctly.

    roughly correlates with "4 - fixstat simulation" although this tests
    actual function and not the simulation.

- TestDirIndex.test_fixstat_with_limitation
    tests rolling back stat changes with limitations correctly.

    roughly correlates with "5 - fixstat simulation with limitation"
    although this tests actual function not the simulation

- TestDirIndex.test_fixstat_with_exclusion
    tests rolling back stat changes with exclusions correctly.

    roughly correlates with "6 - fixstat simulation with exclusion"
    although this tests actual function not the simulation

- TestDirIndex.test_fixstat_with_uid_gid_mapping
    tests rolling back stat changes with uid and gid mapping and that
    uid and gid mapping work in their most basic function.

    correlates with "7 - fixstat with uid and gid"

- TestDirIndex.test_fixstat_with_uid_gid_mapping_rerun
    tests rolling back nothing with uid and gid mapping and ensuring
    no actions are taken.

    correlates with "8 - fixstat repeated - nothing to do"

- TestDirIndex.test_dirindex_comparison_with_limitation
    same as "test_dirindex_delta" but with limitations

    correlates with "9 - dirindex comparison with limitation"

- TestDirIndex.test_dirindex_comparison_with_inverted_limitation
    same as "test_dirindex_comparison_with_limitation" but limitation
    is inverted"

    correlates with "10 - dirindex comparison with inverted limitation"

- TestDirIndex.test_delete
    tests rolling back newly created files (deleting them)

    correlates with "13 - delete"

- TestDirIndex.test_delete_with_limitation
    tests rolling back newly created files (deleting them) with
    limitations

    roughly correlates with "12 - delete simulation with limitation"
    although this tests function not simulation.
- TestDirIndex.test_delete_rerun
    tests attempting to rollback newly created files (deleting them)
    after they've already been deleted. (Should perform no action)

    correlates with "14 - delete repeated - nothing to do"

- TestUserDB.test_userdb_merge_group
    tests the userdb.EtcGroup.merge method and ensures it works
    correctly.

        - ensures no groups lost during merge
        - ensure no duplicate gids exist

    correlates with "15 - merge-userdb passwd"

- TestUserDB.test_userdb_merge_passwd
    tests the userdb.EtcPasswd.merge method and ensures it works
    correctly.

        - ensures no users lost during merge
        - ensure no duplicate uids exist

    correlates with "16 - merge-userdb group"

- TestUserDB.test_userdb_merge
    tests userdb.merge to merge 2 group files and 2 passwd files
    and ensures everything is the same as "test_userdb_merge_group"
    and "test_userdb_merge_passwd"

    roughly correlates with "17 - merge-userdb output maps"

- TestPkgman.test_newpkgs
    test ensures "newpkgs" command works as expected although this is
    probably supurflous considering it's functionality is inherited
    from "set".

    roughly correlates with "18 - newpkgs"

- TestPkgMan.test_newpkgs-install
    tests simulation of `cmd newpkgs --install`

        - ensures non-existant packages get skipped
        - ensures installed packages get ignored
        - ensures installable packages are correct
        - ensures correctness of output command

    correlates with "19 - newpkgs-install simulation"

- TestMysql.test_mysql2fs2mysql_blind
    This is a blind test which checks for any change in sql between
    various conversions.

    Operation:
    1. loads a sql dump into mysql
    2. dumps it back to a sql file
    3. converts the sql file to a tklbam fs representation of a sql dump
    4. converts the tklbam fs representation back into a sql dump
    5. performs a diff between the 3 sql files

    very roughly correlates with tests "20-23"

Missing Tests
-------------

These tests are yet to be fully recreated

- "4 - fixstat simulation" fixstat is being tested but not the simulation
- "5 - fixstat simulation with limitation" fixstat is being tested but not the simulation
- "6 - fixstat simulation with exclusion" fixstat is being tested but not the simulation
- "11 - delete simulation", delete is tested but not it's simulation
- "12 - delete simulation with limitation", delete is tested but not it's simulation
