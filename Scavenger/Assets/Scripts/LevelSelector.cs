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
    private InputField inputField;

    private string levelDirectoryPath;
    private string prefsPath;
    private string[] levelPaths;
    private int numLevelOptions = 3;

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

        inputField = GameObject.FindObjectOfType<InputField>();
        inputField.onEndEdit = new InputField.SubmitEvent();
        inputField.onEndEdit.AddListener(ChangeLevelsDirectory);

        ReadPrefs();

        SetupButtons();
    }

    private void SetupButtons()
    {
        // Get level files
        DirectoryInfo levelDir = new DirectoryInfo(levelDirectoryPath);
        FileInfo[] allLevelFiles = levelDir.GetFiles();
        List<FileInfo> fileList = new List<FileInfo>();
        for (int i = 0; i < allLevelFiles.Length; i++)
            fileList.Add(allLevelFiles[i]);

        levelPaths = new string[numLevelOptions];

        for (int i = 0; i < numLevelOptions; i++)
        {
            int randomFileIndex = Random.Range(0, fileList.Count);
            levelPaths[i] = fileList[randomFileIndex].FullName;
            fileList.RemoveAt(randomFileIndex);
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
        }
        UpdateUI();

    }

    private void SavePrefs()
    {
        File.Delete(prefsPath);
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
        SetupButtons();
        UpdateUI();
    }

    private void UpdateUI()
    {
        levelPathDisplay.text = levelDirectoryPath;
    }
   
}
