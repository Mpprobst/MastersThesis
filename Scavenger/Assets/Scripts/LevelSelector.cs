using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Random = UnityEngine.Random;

public class LevelSelector : MonoBehaviour
{
    public Text levelPathDisplay;
    private LevelButton[] levelButtons;
    private BoardManager boardManager;

    private string levelDirectoryPath;
    private string prefsPath;
    private string[] levelPaths;

    // Start is called before the first frame update
    public void Initialize()
    {
        // create prefereneces if they dont exis
        prefsPath = Application.persistentDataPath + Path.DirectorySeparatorChar + "player_prefs.txt";
        if (!File.Exists(prefsPath))
        {
            levelDirectoryPath = Application.persistentDataPath + Path.DirectorySeparatorChar + "Levels" + Path.DirectorySeparatorChar;
            if (!Directory.Exists(levelDirectoryPath))
            {
                Directory.CreateDirectory(levelDirectoryPath);
            }

           SavePrefs();
        }

        ReadPrefs();

        // Get level files
        DirectoryInfo levelDir = new DirectoryInfo(levelDirectoryPath);
        FileInfo[] allLevelFiles = levelDir.GetFiles();
        int[] fileIndicies = new int[3];
        levelPaths = new string[3];

        for (int i = 0; i < fileIndicies.Length; i++)
        {
            fileIndicies[i] = Random.Range(0, allLevelFiles.Length);
            levelPaths[i] = allLevelFiles[fileIndicies[i]].FullName;
        }

        // Wire up buttons to load levels
        boardManager = GameObject.FindObjectOfType<BoardManager>();
        levelButtons = GetComponentsInChildren<LevelButton>();  
        for (int i = 0; i < levelButtons.Length; i++)
        {
            levelButtons[i].Initialize(levelPaths[i]);
            levelButtons[i].pressedEvent = new StringEvent();
            levelButtons[i].pressedEvent.AddListener(boardManager.LoadLevelFromText);
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void ReadPrefs()
    {
        // TODO: Later on, the levelDirectoryPath will be given by the python routine, not user specified
        using (StreamReader sr = File.OpenText(prefsPath))
        {
            string s = "";
            while ((s = sr.ReadLine()) != null)
            {
                levelDirectoryPath += s;
            }
            Debug.Log("Loading levels from " + levelDirectoryPath);
        }
        UpdateUI();

    }

    private void SavePrefs()
    {
        using (FileStream fs = File.Create(prefsPath))
        {
            Byte[] info = new UTF8Encoding(true).GetBytes(levelDirectoryPath);

            // Add some information to the file.
            fs.Write(info, 0, info.Length);
        }
    }

    public void ChangeLevelsDirectory(string newPath)
    {
        if (newPath == "") return;
        levelDirectoryPath = newPath;
        if (!Directory.Exists(levelDirectoryPath))
        {
            Directory.CreateDirectory(levelDirectoryPath);
        }
        SavePrefs();
        UpdateUI();
    }

    private void UpdateUI()
    {
        levelPathDisplay.text = levelDirectoryPath;
    }
   
}
