﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;

public class StringEvent : UnityEvent<string> { }
public class LevelButton : MonoBehaviour
{
    [System.NonSerialized] public StringEvent pressedEvent;
    public Text levelName;

    private string levelPath;
    private Button button;
    // Start is called before the first frame update
    public void Initialize(string path)
    {
        button = GetComponent<Button>();
        button.onClick = new Button.ButtonClickedEvent();
        button.onClick.AddListener(Pressed);
        levelPath = path;
        levelName.text = System.IO.Path.GetFileNameWithoutExtension(path);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public string GetLevelPath()
    {
        return levelPath;
    }

    private void Pressed()
    {
        Debug.Log("pressed " + levelPath);
        if (pressedEvent != null) pressedEvent.Invoke(levelPath);
    }
}
